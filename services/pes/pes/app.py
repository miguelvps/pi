from flask import Flask, Response, request
from flaskext.sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from common import xml_kinds
from common import modelxmlserializer
from common.xmlserializer_parameters import SERIALIZER_PARAMETERS
from common import search

import urllib
import itertools

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pes.db'
db = SQLAlchemy(app)

serializer_params= SERIALIZER_PARAMETERS
serializer_params['model']['show']= lambda a:   \
    a.model_class.__name__!="Email" and         \
    a.model_class.__name__!="Phone" and         \
    a.model_class.__name__!="Fax"
#only show xml element "list" in lists of Teacher, other lists get appended to parent's xml
serializer_params['list']['show']=lambda a: len(a.l)>0 and a.l[0].__class__.__name__=="Teacher"


class Email(db.Model):
    keywords= ['email','mail']
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column( xml_kinds.email(255) )
    person_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))

    search_atributes= ["email"]
    search_representative="person"


class Phone(db.Model):
    keywords= ['phone','telefone', 'tel']
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column( xml_kinds.phone(255) )
    person_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))

    search_atributes= ["Phone"]
    earch_representative="person"


class Fax(db.Model):
    keywords= ['fax']
    id = db.Column(db.Integer, primary_key=True)
    fax = db.Column( xml_kinds.fax(255) )
    person_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    
    search_atributes= ["fax"]
    earch_representative="person"

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column( xml_kinds.name(1024) )
    birth_date = db.Column( xml_kinds.birthdate )
    office = db.Column( xml_kinds.office(64) )
    emails = db.relationship('Email', backref='person')
    phones = db.relationship('Phone', backref='person')
    faxes = db.relationship('Fax', backref='person')
    
    keywords= ['pessoa','professor']
    search_joins= ["emails", "phones", "faxes"]
    search_atributes= ["name"]

xml_kinds.set_model_kind(Teacher, xml_kinds.person)

@app.route("/")
def search_method():
    q = request.args.get('query', '')   #quoted query
    model_list= [Teacher, Email, Fax, Phone]
    xml= search.service_search_xmlresponse(model_list, q, SERIALIZER_PARAMETERS)
    return Response(response=xml, mimetype="application/xml")


@app.route("/pessoas/", methods=['GET',])
def teachers():
    start = request.args.get('start', 0)
    end = request.args.get('end', 10)
    teachers = Teacher.query.limit(end-start).offset(start).all()
    xml_text= modelxmlserializer.ModelList_xml(teachers).to_xml(SERIALIZER_PARAMETERS).toxml()
    return Response(response=xml_text, mimetype="application/xml")


@app.route("/pessoas/<id>", methods=['GET',])
def teacher(id):
    teacher = Teacher.query.options(joinedload('emails'), joinedload('phones'), joinedload('faxes')).get_or_404(id)
    #import ipdb ; ipdb.set_trace()
    xml_text= modelxmlserializer.Model_Serializer(teacher).to_xml(serializer_params).toprettyxml()
    return Response(response=xml_text, mimetype="application/xml")


if __name__ == "__main__":
    app.run(debug=True, port = 5001)
