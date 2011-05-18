from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy
from common import xml_kinds


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///departamentos.db'
db = SQLAlchemy(app)


course_subjects = db.Table('course_subjects',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'))
)


# DEPARTMENT
class Department(db.Model):
    keyword=[] # TODO: define keywords
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(xml_kinds.dep_name(255))
    acronym = db.Column(xml_kinds.dep_acronym(10))

    courses =  db.relationship('Course', backref='department')


# COURSE
class CourseType(db.Model):
    keyword= [] #TODO define keywords
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(xml_kinds.course_type(255))

    courses = db.relationship('Course', backref='type')


class Course(db.Model):
    keyword=[] # TODO: define keywords
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(xml_kinds.course_name(255))
    acronym = db.Column(xml_kinds.course_acronym(10))
    depatment_id = db.Column (db.Integer, db.ForeignKey('department.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('course_type.id'))

    subjects = db.relationship('Subject', secondary=course_subjects, backref='courses')


# Subject
class SubjectPeriod(db.Model):
    keyword= [] # TODO: define keywords
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(xml_kinds.subject_period(255))

    subjects = db.relationship('Subject', backref='period')


class Subject(db.Model):
    keyword=[] # TODO: define keywords
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(xml_kinds.subject_name(255))
    acronym = db.Column(xml_kinds.subject_acronym(10))
    regent = db.Column(xml_kinds.subject_regent(255))
    coordinator = db.Column(xml_kinds.subject_coordinator(255))
    period_id = db.Column(db.Integer, db.ForeignKey('subject_period.id'))
