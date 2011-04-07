import sys
from flask import Flask, Response
from flaskext.sqlalchemy import SQLAlchemy
sys.path.append('../../common/')
import xml_kinds


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pes.db'
db = SQLAlchemy(app)


class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    email = db.Column( xml_kinds.email(255) )

class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    phone = db.Column( xml_kinds.phone(255) )

class Fax(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    phone = db.Column( xml_kinds.fax(255) )

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column( xml_kinds.name(1024) )
    birth_date = db.Column( xml_kinds.birthdate )
    #contacts = db.relationship('Contact', backref='person', lazy='dynamic')
    office = db.Column( xml_kinds.office(64) )

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
    teacher = Teacher.query.get_or_404(id)
    doc = Document()
    t = doc.createElement("entity")
    doc.appendChild(t)
    t.setAttribute("kind", teacher.__class__.__name__)
    return Response(response=doc.toprettyxml(), mimetype="application/xml")

def init_db():
    import random, os
    if os.path.exists('pes.db'):
      return
    db.create_all()
    for i in range(10):
        b = Teacher('prof %i'%(random.randint(100000,999999)))
        db.session.add(b)
    db.session.commit()

init_db()

if __name__ == "__main__":
    app.run(debug=True)
