from flask import Flask, Response, request
from flaskext.sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from common import xml_kinds
from common import modelxmlserializer
from common.xmlserializer_parameters import SERIALIZER_PARAMETERS
from common.search import match_keywords_to_something

import urllib
import itertools

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pes.db'
db = SQLAlchemy(app)


class Email(db.Model):
    keywords= ['email','mail']
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column( xml_kinds.email(255) )
    person_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))

    @staticmethod
    def search_result(query):
        emails = Email.query.filter(Email.email.like(query)).all()
        return [f.person for f in emails]



class Phone(db.Model):
    keywords= ['phone','telefone', 'tel']
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column( xml_kinds.phone(255) )
    person_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))

    @staticmethod
    def search_result(query):
        phones = Phone.query.filter(Phone.phone.like(query)).all()
        return [f.person for f in phones]


class Fax(db.Model):
    keywords= ['fax']
    id = db.Column(db.Integer, primary_key=True)
    fax = db.Column( xml_kinds.fax(255) )
    person_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))

    @staticmethod
    def search_result(query):
        faxes = Fax.query.filter(Fax.fax.like(query)).all()
        return [f.person for f in faxes]


class Teacher(db.Model):
    keywords= ['pessoa','professor']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column( xml_kinds.name(1024) )
    birth_date = db.Column( xml_kinds.birthdate )
    office = db.Column( xml_kinds.office(64) )

    emails = db.relationship('Email', backref='person')
    phones = db.relationship('Phone', backref='person')
    faxes = db.relationship('Fax', backref='person')

    @staticmethod
    def search_result(query):
        teachers = Teacher.query.options(joinedload('emails'), joinedload('phones'), joinedload('faxes')).filter(Teacher.name.like(query)).all()
        return teachers
        




@app.route("/")
def search():
    query_quoted = request.args.get('query', '')
    query= urllib.unquote_plus(query_quoted)
        
    models= [Phone, Email, Fax, Teacher]
    keywords_models= [(model.keywords, model) for model in models]
    queries_models= match_keywords_to_something(query, keywords_models)

    results=[]
    for targeted_query, model in queries_models:
        db_query= '%{0}%'.format(targeted_query)
        results.append(model.search_result(db_query))
    results= [t for t in itertools.chain(*results)]
    xml_text= modelxmlserializer.ModelList_xml(results).to_xml(SERIALIZER_PARAMETERS).toxml()
    return Response(response=xml_text, mimetype="application/xml")


@app.route("/pessoas/", methods=['GET',])
def teachers():
    teachers = Teacher.query.all()
    xml_text= modelxmlserializer.ModelList_xml(teachers).to_xml(SERIALIZER_PARAMETERS).toxml()
    return Response(response=xml_text, mimetype="application/xml")


@app.route("/pessoas/<id>", methods=['GET',])
def teacher(id):
    teacher = Teacher.query.options(joinedload('emails'), joinedload('phones'), joinedload('faxes')).get_or_404(id)
    xml_text= modelxmlserializer.Model_Serializer(teacher).to_xml(SERIALIZER_PARAMETERS).toprettyxml()
    return Response(response=xml_text, mimetype="application/xml")


if __name__ == "__main__":
    app.run(debug=True, port = 5001)
