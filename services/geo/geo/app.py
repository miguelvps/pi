from flask import Flask, Response, request
from flaskext.sqlalchemy import SQLAlchemy
from common import modelxmlserializer, xmlserializer_parameters
from common import xml_kinds, search

SERIALIZER_PARAMETERS= xmlserializer_parameters.SERIALIZER_PARAMETERS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///geo.db'
db = SQLAlchemy(app)

class PlacemarkType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_name= db.Column(xml_kinds.geo_placemarktypename(64))

    keywords= ["edificios", "salas"]
    search_atributes= ["type_name"]
    search_representative="Placemark"

class Placemark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    folder= db.Column(xml_kinds.geo_folder(128))
    name= db.Column(xml_kinds.geo_name(128))
    abreviation= db.Column(xml_kinds.geo_abreviation(32))
    type_id= db.Column( db.Integer, db.ForeignKey('placemark_type.id'))
    type= db.relationship('PlacemarkType')
    geowkt= db.Column(xml_kinds.geo_wkt(8192))

    keywords= ['sitio','place', 'placemark', 'edificio', 'sala' ]
    search_joins= ["type"]
    search_atributes= ["folder", "name", "abreviation"]

xml_kinds.set_model_kind(Placemark, xml_kinds.geo_placemark)
xml_kinds.set_model_kind(PlacemarkType, xml_kinds.geo_placemarktype)

@app.route("/placemark/", methods=['GET',])
def placemark():
    placemarks = Placemark.query.all()
    xml_text= modelxmlserializer.ModelList_xml(placemarks).to_xml(SERIALIZER_PARAMETERS).toxml()
    return Response(response=xml_text, mimetype="application/xml")

@app.route("/")
def search_method():
    q = request.args.get('query', '')   #quoted query
    model_list= [Placemark, PlacemarkType]
    xml= search.service_search_xmlresponse(model_list, q, SERIALIZER_PARAMETERS)
    return Response(response=xml, mimetype="application/xml")
