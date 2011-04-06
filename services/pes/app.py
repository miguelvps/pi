from flask import Flask, Response
from flaskext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pes.db'
db = SQLAlchemy(app)

class birthdate(db.Date): kind = "string"
class name(db.String): pass
class office(db.String): pass
class contact(db.String): pass
class email(db.String): pass
class phone(db.String): pass
class fax(db.String): pass

#class Contact_Type(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    #type = db.Column(db.String(64), unique=True)

#class Contact(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    #person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    #type_id = db.Column(db.Integer, db.ForeignKey('contact_type.id'))
    #contact = db.Column(Contact(64))

class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    email = db.Column(email(255))

class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    phone = db.Column(phone(255))

class Fax(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    phone = db.Column(fax(255))

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(name(1024))
    birth_date = db.Column(birthdate)
    #contacts = db.relationship('Contact', backref='person', lazy='dynamic')
    office = db.Column(office(64))

    def __init__(self, name):
        self.name = name

"""
<entity>
    <entity kind="person">
        <entity kind="name" type="string">Nome</entity>
        <entity kind="birth_date" type="string">01-01-1900</entity>
        <entity kind="birth_date" type="string">01-01-1900</entity>
    </entity>
</entity>
"""

from xml.dom.minidom import Document

@app.route("/pessoas/", methods=['GET',])
def teachers():
    pass

@app.route("/pessoas/<id>", methods=['GET',])
def teacher(id):
    #teacher = Teacher.query.get_or_404(id)
    doc = Document()
    t = doc.createElement("entity")
    doc.appendChild(t)
    t.setAttribute("kind", teacher.__class__.__name__)
    return Response(response=doc.toprettyxml(), mimetype="application/xml")

if __name__ == "__main__":
    app.run(debug=True)
