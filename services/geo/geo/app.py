from flask import Flask, Response, request
from flaskext.sqlalchemy import SQLAlchemy
from common import xser, xser_parameters, xml_attributes
from common import xml_kinds, search, xser_property, xml_types, xml_names
from common.xml_kinds import KIND_PROP_NAME
from common.xml_types import TYPE_PROP_NAME
from common.xml_names import NAME_PROP_NAME

SERIALIZER_PARAMETERS= xser_parameters.SERIALIZER_PARAMETERS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///geo.db'
db = SQLAlchemy(app)

class PlacemarkType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_name= db.Column(xml_attributes.geo_placemarktype_name(64))

    keywords= ['edificios', 'salas']
    search_atributes= ["type_name"]
    search_representative="placemark"

class Placemark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    folder= db.Column(xml_attributes.geo_placemark_folder(128))
    name= db.Column(xml_attributes.geo_placemark_name(128))
    abreviation= db.Column(xml_attributes.geo_placemark_abreviation(32))
    type_id= db.Column( db.Integer, db.ForeignKey('placemark_type.id'))
    type= db.relationship('PlacemarkType', backref='placemark')
    geowkt= db.Column(xml_attributes.geo_placemark_wkt(8192))

    keywords= ['sitio','place', 'placemark', 'sala', 'edificio']
    search_joins= ["type"]
    search_atributes= ["name", "abreviation"]
    
xser_property.set_xser_prop(Placemark, KIND_PROP_NAME, xml_kinds.placemark)
xser_property.set_xser_prop(Placemark, TYPE_PROP_NAME, xml_types.LIST_TYPE)
xser_property.set_xser_prop(Placemark, NAME_PROP_NAME ,xml_names.geo_placemark)
#xser_property.set_xser_prop(PlacemarkType, KIND_PROP_NAME, xml_kinds.placemarktype)
#xser_property.set_xser_prop(PlacemarkType, TYPE_PROP_NAME, xml_types.LIST_TYPE)

@app.route("/placemarks/", methods=['GET',])
def placemark():
    placemarks = Placemark.query.all()
    xml_text= xser.ModelList_xml(placemarks).to_xml(SERIALIZER_PARAMETERS).toxml()
    return Response(response=xml_text, mimetype="application/xml")

@app.route("/")
def search_method():
    q = request.args.get('query', '')   #quoted query
    model_list= [Placemark, PlacemarkType]
    xml= search.service_search_xmlresponse(model_list, q, SERIALIZER_PARAMETERS)
    return Response(response=xml, mimetype="application/xml")
