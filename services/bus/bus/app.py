from flask import Flask, Response, request
from flaskext.sqlalchemy import SQLAlchemy
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
        xml+= '<entity type="string" service="%s" url="/transportation?destination_lat=%s&amp;destination_long%s">%s</entity>' % (SERVICE_NAME, l, ln, location_str)
    xml+="</entity>"
    return xml
    
@app.route("/transport/transportation")
def destination():
    l1= request.args.get('lat', '')
    ln1= request.args.get('long', '')
    l2= request.args.get('destination_lat', '')
    ln2= request.args.get('destination_long', '')
    if not all((l1, ln1, l2, ln2)):
        xml=""
    else:
        now= datetime.datetime.now()
        j= transporlis.transportation(l1,ln1,l2,ln2, now)
        
    

@app.route("/")
def search_method():
    query= urllib.unquote_plus(request.args.get('query', ''))
    if not "transportes " in query:
        xml=""
    else:
        locationstr= query[12:]
        
        locations= transporlis.geolocate(locationstr)
        xml= locations_to_xml(locations)
        
    return Response(response=xml, mimetype="application/xml")
