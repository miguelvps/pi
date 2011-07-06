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
    return xml
    
@app.route("/transport/transportation")
def destination():
    import ipdb; ipdb.set_trace()
    latlng= urllib.unquote_plus(request.args.get(str(LATLNG), ''))
    dlatlng= urllib.unquote_plus(request.args.get('destination_latlng', ''))
    try:
        l1, ln1= latlng.split(",")
        l2, ln2= dlatlng.split(",")
        assert all((l1, ln1, l2, ln2))
        now= datetime.datetime.now()
        j= transporlis.transportation(l1,ln1,l2,ln2, now)
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
