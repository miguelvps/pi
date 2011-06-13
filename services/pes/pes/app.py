from flask import Flask, Response, request, url_for
from flaskext.sqlalchemy import SQLAlchemy

from common import search


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pes.db'
app.config.from_envvar('SETTINGS', silent=True)
db = SQLAlchemy(app)


class Email(db.Model):
    keywords= ['email','mail']
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))

    search_atributes= ["email"]
    search_representative="person"


class Phone(db.Model):
    keywords= ['phone','telefone', 'tel']
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(255))
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))

    search_atributes= ["Phone"]
    earch_representative="person"


class Fax(db.Model):
    keywords= ['fax']
    id = db.Column(db.Integer, primary_key=True)
    fax = db.Column(db.String(255))
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))

    search_atributes= ["fax"]
    earch_representative="person"

class Person(db.Model):
    keywords= ['pessoa','professor']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1024))
    birth_date = db.Column(db.Date)
    office = db.Column(db.String(64))

    emails = db.relationship('Email', backref='person')
    phones = db.relationship('Phone', backref='person')
    faxes = db.relationship('Fax', backref='person')

    search_joins= ["emails", "phones", "faxes"]
    search_atributes= ["name"]

    def permalink(self):
        return url_for('person', id=self.id)

    def to_xml_shallow(self):
        return '<entity type="string" service="Pessoas" url="%s">%s</entity>' % (self.permalink(), self.name)

    def to_xml(self):
        xml = '<entity type="record">'
        xml += '<entity kind="person" type="string">%s</entity>' % self.name
        xml += '<entity type="string">%s</entity>' % self.birth_date if self.birth_date else ''
        xml += '<entity kind="placemark" type="string">%s</entity>' % self.office if self.office else ''
        xml += '<entity name="Emails" type="list">'
        if self.emails:
            for email in self.emails:
                xml += '<entity type="email">%s</entity>' % email.email
            xml += '</entity>'
        if self.phones:
            xml += '<entity name="Phones" type="list">'
            for phone in self.phones:
                xml += '<entity kind="phone" type="string">%s</entity>' % phone.phone
            xml += '</entity>'
        if self.faxes:
            xml += '<entity name="Faxes" type="list">'
            for fax in self.faxes:
                xml += '<entity kind="fax" type="string">%s</entity>' % fax.fax
            xml += '</entity>'
        xml += '</entity>'
        return xml


@app.route("/")
def search_method():
    q = request.args.get('query', '')   #quoted query
    model_list= [Person, Email, Fax, Phone]
    xml= search.service_search_xmlresponse(model_list, q)
    # TODO: search
    return Response(response=xml, mimetype="application/xml")


@app.route("/pessoas", methods=['GET',])
def persons():
    start = int(request.args.get('start', 0))
    end = int(request.args.get('end', 10))
    persons = Person.query.limit(end-start).offset(start).all()
    xml = '<entity type="list">'
    for p in persons:
        xml += p.to_xml_shallow()
    xml += '</entity>'
    return Response(response=xml, mimetype="application/xml")


@app.route("/pessoas/<id>", methods=['GET',])
def person(id):
    person = Person.query.get_or_404(id)
    return Response(response=person.to_xml(), mimetype="application/xml")
