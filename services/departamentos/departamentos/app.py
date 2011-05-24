# -*- coding: utf-8 -*-

from flask import Flask, Response, request
from flaskext.sqlalchemy import SQLAlchemy
from common import xml_kinds
from common import modelxmlserializer
from common.xmlserializer_parameters import SERIALIZER_PARAMETERS
from common import search


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///departamentos.db'
db = SQLAlchemy(app)


course_subjects = db.Table('course_subjects',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'))
)


# DEPARTMENT
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(xml_kinds.dep_name(255))

    courses =  db.relationship('Course', backref='department')

    keywords = ['departamento', 'departamentos']
    search_atributes = ['name']

xml_kinds.set_model_kind(Department, xml_kinds.department)


# COURSE
class CourseType(db.Model):
    keywords = ['licenciatura', 'licenciaturas', 'mestrado', 'mestrados',
               'douturamento', 'douturamento']
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(xml_kinds.course_type(255))

    courses = db.relationship('Course', backref='type')

    search_atributes = ['name']
    search_representative = 'courses'


class Course(db.Model):
    keywords=['curso', 'cursos']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(xml_kinds.course_name(255))
    acronym = db.Column(xml_kinds.course_acronym(10))
    depatment_id = db.Column (db.Integer, db.ForeignKey('department.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('course_type.id'))

    subjects = db.relationship('Subject', secondary=course_subjects, backref='courses')

    search_atributes = ['name', 'acronym']
    search_join = ['type']

xml_kinds.set_model_kind(Course, xml_kinds.course)


class Subject(db.Model):
    keywords=['cadeira', 'cadeiras', 'disciplina', 'disciplinas']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(xml_kinds.subject_name(255))
    acronym = db.Column(xml_kinds.subject_acronym(10))
    regent = db.Column(xml_kinds.subject_regent(255))
    coordinator = db.Column(xml_kinds.subject_coordinator(255))
    period = db.Column(db.Enum(u'Anual', u'1º Sem', u'2º Sem',
                               u'1º Tri', u'2º Tri', u'3º Tri'))

    search_atributes = ['name', 'acronym']

xml_kinds.set_model_kind(Subject, xml_kinds.subject)


@app.route('/')
def s():
    q = request.args.get('query', '')   #quoted query
    xml= search.service_search_xmlresponse([Department, Course, CourseType, Subject], q, SERIALIZER_PARAMETERS)
    return Response(response=xml, mimetype="application/xml")

@app.route('/departamentos')
def departments():
    departments = Department.query.all()
    xml_text= modelxmlserializer.ModelList_xml(departments).to_xml(SERIALIZER_PARAMETERS).toxml()
    return Response(xml_text, mimetype='application/xml')

@app.route('/departamentos/<id>')
def department(id):
    department = Department.query.get_or_404(id)
    xml_text= modelxmlserializer.Model_Serializer(department).to_xml(SERIALIZER_PARAMETERS).toprettyxml()
    return Response(xml_text, mimetype='application/xml')

@app.route('/cursos')
def courses():
    courses = Course.query.all()
    xml_text= modelxmlserializer.ModelList_xml(courses).to_xml(SERIALIZER_PARAMETERS).toxml()
    return Response(xml_text, mimetype='application/xml')

@app.route('/cursos/<id>')
def course(id):
    course = Course.query.get_or_404(id)
    xml_text= modelxmlserializer.Model_Serializer(course).to_xml(SERIALIZER_PARAMETERS).toprettyxml()
    return Response(xml_text, mimetype='application/xml')

@app.route('/cadeiras')
def subjects():
    subjects = Subject.query.all()
    xml_text= modelxmlserializer.ModelList_xml(subjects).to_xml(SERIALIZER_PARAMETERS).toxml()
    return Response(xml_text, mimetype='application/xml')

@app.route('/cadeiras/<id>')
def subject(id):
    subject = Subject.query.get_or_404(id)
    xml_text= modelxmlserializer.Model_Serializer(subject).to_xml(SERIALIZER_PARAMETERS).toprettyxml()
    return Response(xml_text, mimetype='application/xml')
