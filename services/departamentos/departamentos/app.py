# -*- coding: utf-8 -*-

from flask import Flask, Response, request, url_for
from flaskext.sqlalchemy import SQLAlchemy
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
    name = db.Column(db.String(255))

    courses =  db.relationship('Course', backref='department')

    keywords = ['departamento', 'departamentos' 'department']
    search_atributes = ['name']

    def permalink(self):
        return url_for('department', id=self.id)

    def to_xml_shallow(self):
        return '<entity type="string" service="Departamentos" url="%s">%s</entity>' %(self.permanlink(), self.name)

    def to_xml(self):
        xml = '<entity type="record">'
        xml += '<entity type="string">%s</entity>' %self.name
        if courses:
            xml += '<entity type="list" name="Cursos">'
            for course in courses:
                xml += '<entity type="string" service="Departamentos" url="%s">%s</entity>' % (course.permalink(), course.name)
            xml += '</entity>'       
        xml += '</entity>'
        return xml

# COURSE
class CourseType(db.Model):
    keywords = ['licenciatura', 'licenciaturas', 'mestrado', 'mestrados',
               'douturamento', 'douturamento']
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(255))
    courses = db.relationship('Course', backref='type')

    search_atributes = ['name']
    search_representative = 'courses'


class Course(db.Model):
    keywords=['curso', 'cursos']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    acronym = db.Column(db.String(10))
    depatment_id = db.Column (db.Integer, db.ForeignKey('department.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('course_type.id'))

    subjects = db.relationship('Subject', secondary=course_subjects, backref='courses')

    search_atributes = ['name', 'acronym']
    search_join = ['type']
    
    def permalink(self):
        return url_for('course', id=self.id)

    def to_xml_shallow(self):
        return '<entity type="string" service="Departamentos" url="%s">%s</entity>' % (self.permanlink(), self.name)

    def to_xml(self):
        xml = '<entity type="record">'
        xml += '<entity type="string">%s</entity>' % self.name
        xml += '<entity type="string" name="acronimo">%s</entity>' % self.acronym
        xml += '<entity type="string" service ="Departamentos" url="%s" name="Departamento">%s</entity>' % (self.department.permalink(), self.department.name)
        if subjects:
            xml += '<entity type="list" name="Cadeiras">'
            for subject in subjects:
                xml += '<entity type="string" service="Departamentos" url="%s">%s</entity>' % (subject.permalink(), subject.name)
            xml += '<entity>'
        if self.type:
            xml += '</entity type="string"> %s</entity>' % type.name
        xml += '</entity>'
        return xml


class Subject(db.Model):
    keywords=['cadeira', 'cadeiras', 'disciplina', 'disciplinas']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    acronym = db.Column(db.String(10))
    regent = db.Column(db.String(255))
    coordinator = db.Column(db.String(255))
    period = db.Column(db.Enum(u'Anual', u'1º Sem', u'2º Sem',
                               u'1º Tri', u'2º Tri', u'3º Tri'))

    search_atributes = ['name', 'acronym']

    def permalink(self):
        return url_for('subject', id=self.id)

    def to_xml_shallow(self):
        return '<entity type="string" service="Departamentos" url="%s">%s</entity>' %(self.permanlink(), self.name)

    def to_xml(self):
        xml = '<entity type="record">'
        xml += '<entity type="string">%s</entity>' %self.name
        xml += '<entity type="string">%s</entity>' %self.acronym
        xml += '<entity kind="person" type="string" name="Regente">%s</entity>' %self.regent
        xml += '<entity kind="person" type="string" name="Coordenador">%s</entity>' %self.coordinator
        xml += '<entity type="string" name="Periodo">%s</entity>' % self.period
        if courses:
            xml += '<entity type="list" name="Cursos">'
            for course in courses:
                xml += '<entity type="string" service="Departamentos" url="%s">%s</entity>' % (course.permalink(), course.name)
            xml += '</entity>'
        xml += '</entity>'
        return xml



@app.route('/')
def s():
    q = request.args.get('query', '')   #quoted query
    xml= search.service_search_xmlresponse([Department, Course, CourseType, Subject], q, SERIALIZER_PARAMETERS)
    return Response(response=xml, mimetype="application/xml")

@app.route('/departamentos')
def departments():
    start = request.args.get('start', 0)
    end = request.args.get('end', 10)
    departments = Department.query.limit(end-start).offset(start).all()
    xml_text= xser.ModelList_xml(departments).to_xml(SERIALIZER_PARAMETERS).toxml()
    return Response(xml_text, mimetype='application/xml')

@app.route('/departamentos/<id>')
def department(id):
    department = Department.query.get_or_404(id)
    xml_text= xser.Model_Serializer(department).to_xml(SERIALIZER_PARAMETERS).toprettyxml()
    return Response(xml_text, mimetype='application/xml')

@app.route('/cursos')
def courses():
    start = request.args.get('start', 0)
    end = request.args.get('end', 10)
    courses = Course.query.limit(end-start).offset(start).all()
    xml_text= xser.ModelList_xml(courses).to_xml(SERIALIZER_PARAMETERS).toxml()
    return Response(xml_text, mimetype='application/xml')

@app.route('/cursos/<id>')
def course(id):
    course = Course.query.get_or_404(id)
    xml_text= xser.Model_Serializer(course).to_xml(SERIALIZER_PARAMETERS).toprettyxml()
    return Response(xml_text, mimetype='application/xml')

@app.route('/cadeiras')
def subjects():
    start = request.args.get('start', 0)
    end = request.args.get('end', 10)
    subjects = Subject.query.limit(end-start).offset(start).all()
    xml_text= xser.ModelList_xml(subjects).to_xml(SERIALIZER_PARAMETERS).toxml()
    return Response(xml_text, mimetype='application/xml')

@app.route('/cadeiras/<id>')
def subject(id):
    subject = Subject.query.get_or_404(id)
    xml_text= xser.Model_Serializer(subject).to_xml(SERIALIZER_PARAMETERS).toprettyxml()
    return Response(xml_text, mimetype='application/xml')
