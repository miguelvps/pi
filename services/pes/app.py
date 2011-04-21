import sys
from flask import Flask, Response
from flaskext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload

sys.path.append('../../common/')
import xml_kinds
import modelxmlserializer
from xmlserializer_parameters import SERIALIZER_PARAMETERS


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pes.db'
db = SQLAlchemy(app)


class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column( xml_kinds.email(255) )
    person_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))


class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column( xml_kinds.phone(255) )
    person_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))


class Fax(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fax = db.Column( xml_kinds.fax(255) )
    person_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column( xml_kinds.name(1024) )
    birth_date = db.Column( xml_kinds.birthdate )
    office = db.Column( xml_kinds.office(64) )

    emails = db.relationship('Email', backref='person')
    phones = db.relationship('Phone', backref='person')
    faxes = db.relationship('Fax', backref='person')


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
    app.run(debug=True)
