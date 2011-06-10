from flask import Flask, Response, request
from flaskext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sps.db'
db = SQLAlchemy(app)


class Deadline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    date = db.Coumn(db.Datetime)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))


class Requisite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    url = db.Column(db.String(2083))
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))


class Process(db.Model):
    id = db.column(db.Integer, primary_key=True)
    url = db.Column(db.String(2083))
    info = db.Column(db.Text)

    deadlines = db.relationship('Deadline', backref='process')
    requisites = db.relationship('Requisite', backref='process')
    documents = db.relationship('Document', backref='document')


@app.route("/")
def search():
    pass
