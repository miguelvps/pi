from flask import Flask, Response, request
from flaskext.sqlalchemy import SQLAlchemy

from common import xml_kinds

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///geo.db'
db = SQLAlchemy(app)

class PlacemarkType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_name= db.Column(db.String(64))

class Placemark(db.Model):
    keywords= []
    id = db.Column(db.Integer, primary_key=True)
    folder= db.Column(db.String(128))
    name= db.Column(xml_kinds.geo_name(128))
    abreviation= db.Column(db.String(32))
    type_id= db.Column( db.Integer, db.ForeignKey('placemark_type.id'))
    type= db.relationship('PlacemarkType')
    geowkt= db.Column(db.String(8192))

xml_kinds.set_model_kind(Placemark, xml_kinds.geo_placemark)
