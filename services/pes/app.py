from flask import Flask, Response
from flaskext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pes.db'
db = SQLAlchemy(app)

STRING_TYPE= "string"
NUMBER_TYPE= "number"
DATETIME_TYPE= "datetime"
EMAIL_TYPE= "email"
URL_TYPE= "url"
COORDINATE_TYPE= "coordinate"
IMAGE_TYPE= "image"
VIDEO_TYPE= "video"


class birthdate(db.Date): type = DATETIME_TYPE
class name(db.String): type = STRING_TYPE
class office(db.String): type = STRING_TYPE
class contact(db.String): type = STRING_TYPE
class email(db.String): type = EMAIL_TYPE
class phone(db.String): type = STRING_TYPE
class fax(db.String): type = STRING_TYPE




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
