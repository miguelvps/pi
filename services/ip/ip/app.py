from flask import Flask, Response, request, url_for
from flaskext.sqlalchemy import SQLAlchemy

from common import search


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ip.db'
app.config.from_envvar('SETTINGS', silent=True)
db = SQLAlchemy(app)


class Deadline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(2048))
    date = db.Column(db.Date)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))

    def to_xml_full(self):
        return '<entity type="string">%s: %s</entity>'% (self.name, self.date.strftime("%D/%M/%Y"))


class Requisite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256))
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))

class RequisiteDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256))
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))


class Document(db.Model):
    keywords = ['documento', 'documentos']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    url = db.Column(db.String(2083))
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))

    def to_xml_full(self):
        return '<entity name="%s" type="url">%s</entity>'% (self.name, self.url)


class Process(db.Model):
    keywords = ['processo', 'processos']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    url = db.Column(db.String(2083))
    info = db.Column(db.Text)

    deadlines = db.relationship('Deadline', backref='process')
    requisites = db.relationship('Requisite', backref='process')
    documents = db.relationship('Document', backref='process')
    requisite_documents = db.relationship('RequisiteDocument', backref='process')

    def permalink(self):
        return url_for('process', id=self.id)

    def to_xml_shallow(self):
        return '<entity type="string" service="IP" url="%s">%s</entity>' % (self.permalink(), self.name)

    def to_xml_full(self):
        xml= u'<entity type="record">'
        xml+= u'<entity type="string">%s</entity>' % self.name
        xml+= u'<entity name="Página do Processo" type="url">%s</entity>' % self.url
        if self.info: xml+= u'<entity type="string">%s</entity>' % self.info             #<-----TYPE URL NOT DEFINED!
        if self.documents:
            xml+= u'<entity name="Documentos Informativos" type="list">'
            for doc in self.documents:
                doc.to_xml_full()
            xml+= u'</entity>'
        if self.requisite_documents:
            xml+= u'<entity name="Documentos Necessários" type="list">'
            for rd in self.requisite_documents:
                xml+= u'<entity type="string">%s</entity>' % (rd.description)
            xml+= u'</entity>'
        if self.requisites:
            xml+= u'<entity name="Requisitos" type="list">'
            for req in self.requisites:
                xml+= u'<entity type="string">%s</entity>' % (req.description)
            xml+= u'</entity>'
        xml+='</entity>'
        return xml
        
@app.route("/")
def s():
    q = request.args.get('query', '')   #quoted query
    model_list= [Document, Process]
    xml= search.service_search_xmlresponse(model_list, q)
    return Response(response=xml, mimetype="application/xml")

@app.route("/process")
def processes():
    start = int(request.args.get('start', 0))
    end = int(request.args.get('end', 10))
    process = Process.query.limit(end-start).offset(start).all()
    xml = '<entity type="list">'
    for p in process:
        xml += p.to_xml_shallow()
    xml += '</entity>'
    return Response(response=xml, mimetype="application/xml")

@app.route("/process/<id>")
def process(id):
    process = Process.query.get_or_404(id)
    return Response(response=process.to_xml_full(), mimetype="application/xml")
