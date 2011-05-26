from flask import Flask, Response, request
from flaskext.sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from common import xml_kinds
from common import xser
from common.xser_parameters import SERIALIZER_PARAMETERS
from common.xser_property import set_xser_prop
from common import search

import urllib
import itertools

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pes.db'
db = SQLAlchemy(app)

serializer_params= SERIALIZER_PARAMETERS

class Email(db.Model):
    keywords= ['email','mail']
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column( db.String(255) )
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))

    set_xser_prop( email, 'kind', xml_kinds.pes_person_email)
    search_atributes= ["email"]
    search_representative="person"


class Phone(db.Model):
    keywords= ['phone','telefone', 'tel']
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column( db.String(255) )
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))

    set_xser_prop( phone, 'kind', xml_kinds.pes_person_phone)
    search_atributes= ["Phone"]
    earch_representative="person"


class Fax(db.Model):
    keywords= ['fax']
    id = db.Column(db.Integer, primary_key=True)
    fax = db.Column( db.String(255) )
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))

    set_xser_prop( fax, 'kind', xml_kinds.pes_person_fax)
    search_atributes= ["fax"]
    earch_representative="person"

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column( db.String(1024) )
    birth_date = db.Column( db.DateTime )
    office = db.Column( db.String(64) )
    emails = db.relationship('Email', backref='person')
    phones = db.relationship('Phone', backref='person')
    faxes = db.relationship('Fax', backref='person')

    set_xser_prop( name, 'kind', xml_kinds.pes_person_name)

    keywords= ['pessoa','professor']
    search_joins= ["emails", "phones", "faxes"]
    search_atributes= ["name"]

set_xser_prop(Person, 'kind', xml_kinds.pes_person)

@app.route("/")
def search_method():
    q = request.args.get('query', '')   #quoted query
    model_list= [Person, Email, Fax, Phone]
    xml= search.service_search_xmlresponse(model_list, q, SERIALIZER_PARAMETERS)
    return Response(response=xml, mimetype="application/xml")


@app.route("/pessoas/", methods=['GET',])
def persons():
    start = request.args.get('start', 0)
    end = request.args.get('end', 10)
    persons = Person.query.limit(end-start).offset(start).all()
    xml_text= xser.ModelList_xml(persons).to_xml(SERIALIZER_PARAMETERS).toxml()
    return Response(response=xml_text, mimetype="application/xml")


@app.route("/pessoas/<id>", methods=['GET',])
def person(id):
    person = Person.query.options(joinedload('emails'), joinedload('phones'), joinedload('faxes')).get_or_404(id)
    xml_text= xser.Model_Serializer(person).to_xml(serializer_params).toprettyxml()
    return Response(response=xml_text, mimetype="application/xml")
