from flask import Flask, Response, request
from flaskext.sqlalchemy import SQLAlchemy
from common.rest_method_parameters import LATLNG
import urllib
import datetime

from transporlis import transporlis


SERVICE_NAME= "Bus"
app = Flask(__name__)
app.config.from_envvar('SETTINGS', silent=True)



def locations_to_xml(locations):
    xml= '<entity type="list">'
    for location in locations:
        l= location[0]
        ln= location[1]
        location_str= location[2]
        xml+= '<entity type="string" service="%s" url="/transport/transportation?destination_latlng=%s">%s</entity>' % (SERVICE_NAME, l+","+ln, location_str)
    xml+="</entity>"
    xml= xml.replace("&","&amp;")
    return xml


def journey_to_xml(j):
    transports_names= ["%s (%s)"%(t.operator, t.operator_type) for t in j.transports]
        
    pairs= []   #pairs of geowkt, text
    for t in j.transports:
        first=True
        for i,path in enumerate(t.paths):
            if first:
                first=False
                s= u"%s (%s)  %s-%s  %.2f€\t%.0fg CO2" % (t.operator, t.operator_type, t.start_time.strftime("%H:%M"), t.end_time.strftime("%H:%M"), t.cost, t.co2)
            else:
                s="%s - %i/%i"%(t.operator, i+1, len(t.paths))
            geowkt="POLYLINE((%s))" % (", ".join(["%f %f"%(c.y,c.x) for c in path.l]))
            pairs.append( (geowkt, s) )

    
    xml = '<entity type="map">'
    xml += '<entity type="string">%s</entity>' %"Viagem"
    for geowkt, s in pairs:
        xml += '<entity type="geowkt">%s</entity>' % (geowkt)
        xml += '<entity type="string">%s</entity>' % (s)
    xml += '</entity>'
    xml= xml.replace("&","&amp;")
    return xml
    
@app.route("/transport/transportation")
def destination():
    latlng= urllib.unquote_plus(request.args.get("latlng", ''))
    dlatlng= urllib.unquote_plus(request.args.get('destination_latlng', ''))
    try:
        l1, ln1= latlng.split(",")
        l2, ln2= dlatlng.split(",")
        assert all((l1, ln1, l2, ln2))
        now= datetime.datetime.now()
        j= transporlis.transportation(l1,ln1,l2,ln2, now)
        xml=journey_to_xml(j)
    except:
        xml=""
    return Response(response=xml, mimetype="application/xml")
    

@app.route("/")
def search_method():
    query= urllib.unquote_plus(request.args.get('query', ''))
    try:
        assert "transportes " in query
        locationstr= query[12:]
        
        locations= transporlis.geolocate(locationstr)
        xml= locations_to_xml(locations)
    except:
        xml=""
    return Response(response=xml, mimetype="application/xml")
