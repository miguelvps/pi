from flask import Flask, Response, request, url_for
from flaskext.sqlalchemy import SQLAlchemy

from common import search


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ip.db'
db = SQLAlchemy(app)


class Deadline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    date = db.Column(db.Date)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))


class Requisite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))


class Document(db.Model):
    keywords = ['documento', 'documentos']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    url = db.Column(db.String(2083))
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))


class Process(db.Model):
    keywords = ['processo', 'processos']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    url = db.Column(db.String(2083))
    info = db.Column(db.Text)

    deadlines = db.relationship('Deadline', backref='process')
    requisites = db.relationship('Requisite', backref='process')
    documents = db.relationship('Document', backref='document')

    def permalink(self):
        return url_for('processes', id=self.id)

    def to_xml_shallow(self):
        return '<entity type="string" service="IP" url="%s">%s</entity>' % (self.permalink(), self.name)

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
    return Response(response=process.to_xml(), mimetype="application/xml")
