# -*- coding: utf-8 -*-

from flask import Flask, Response, request, url_for
from flaskext.sqlalchemy import SQLAlchemy
from flaskext.babel import Babel, gettext as _
from common import search


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///departamentos.db'
app.config.from_envvar('SETTINGS', silent=True)
db = SQLAlchemy(app)
babel = Babel(app)


@babel.localeselector
def get_locale():
    lang = request.args.get('lang')
    return lang or request.accept_languages.best_match(['pt', 'en'])


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
        return '<entity type="string" service="Departamentos" url="%s">%s</entity>' %(self.permalink(), self.name)

    def to_xml(self):
        xml = '<entity type="record">'
        xml += '<entity type="string">%s</entity>' %self.name
        if self.courses:
            xml += '<entity type="list" name="%s">' % (_('Cursos'))
            for course in self.courses:
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
        return '<entity type="string" service="Departamentos" url="%s">%s</entity>' % (self.permalink(), self.name)

    def to_xml(self):
        xml = '<entity type="record">'
        xml += '<entity type="string">%s</entity>' % self.name
        xml += u'<entity type="string" name="%s">%s</entity>' % (_(u'Acrónimo'), self.acronym)
        if self.type:
            xml += '<entity name="%s" type="string">%s</entity>' % (_('Tipo'), self.type.name)
        xml += '<entity type="string" service ="Departamentos" url="%s" name="%s">%s</entity>' % (self.department.permalink(), _('Departamento'), self.department.name)
        if self.subjects:
            xml += '<entity type="list" name="%s">' % (_('Cadeiras'))
            for subject in self.subjects:
                xml += '<entity type="string" service="Departamentos" url="%s">%s</entity>' % (subject.permalink(), subject.name)
            xml += '</entity>'
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
                               u'1º Tri', u'2º Tri', u'3º Tri', period_enum="teste"))

    search_atributes = ['name', 'acronym']

    def permalink(self):
        return url_for('subject', id=self.id)

    def to_xml_shallow(self):
        return '<entity type="string" service="Departamentos" url="%s">%s</entity>' %(self.permalink(), self.name)

    def to_xml(self):
        xml = '<entity type="record">'
        xml += '<entity type="string">%s</entity>' %self.name
        xml += u'<entity type="string" name="%s">%s</entity>' % (_(u'Acrónimo'), self.acronym)
        xml += '<entity kind="pessoa" type="string" name="%s">%s</entity>' % (_('Regente'), self.regent)
        xml += '<entity kind="pessoa" type="string" name="%s">%s</entity>' % (_('Coordenador'), self.coordinator)
        xml += '<entity type="string" name="%s">%s</entity>' % (_('Periodo'), self.period)
        if self.courses:
            xml += '<entity type="list" name="%s">' % (_('Cursos'))
            for course in self.courses:
                xml += '<entity type="string" service="Departamentos" url="%s">%s</entity>' % (course.permalink(), course.name)
            xml += '</entity>'
        xml += '</entity>'
        return xml


@app.route('/')
def s():
    q = request.args.get('query', '')   #quoted query
    model_list= [Department, Course, CourseType, Subject]
    xml= search.service_search_xmlresponse(model_list, q)
    return Response(response=xml, mimetype="application/xml")

@app.route('/departamentos')
def departments():
    start = int(request.args.get('start', 0))
    end = int(request.args.get('end', 10))
    departments = Department.query.limit(end-start).offset(start).all()
    xml = '<entity type="list">'
    for d in departments:
        xml += d.to_xml_shallow()
    xml += '</entity>'
    return Response(xml, mimetype='application/xml')

@app.route('/departamentos/<id>')
def department(id):
    department = Department.query.get_or_404(id)
    return Response(response=department.to_xml(), mimetype='application/xml')

@app.route('/cursos')
def courses():
    start = int(request.args.get('start', 0))
    end = int(request.args.get('end', 10))
    courses = Course.query.limit(end-start).offset(start).all()
    xml = '<entity type="list">'
    for c in courses:
        xml += c.to_xml_shallow()
    xml += '</entity>'
    return Response(xml, mimetype='application/xml')

@app.route('/cursos/<id>')
def course(id):
    course = Course.query.get_or_404(id)
    return Response(response = course.to_xml(), mimetype='application/xml')

@app.route('/cadeiras')
def subjects():
    start = int(request.args.get('start', 0))
    end = int(request.args.get('end', 10))
    subjects = Subject.query.limit(end-start).offset(start).all()
    xml = '<entity type="list">'
    for s in subjects:
        xml += s.to_xml_shallow()
    xml += '</entity>'
    return Response(xml, mimetype='application/xml')

@app.route('/cadeiras/<id>')
def subject(id):
    subject = Subject.query.get_or_404(id)
    return Response(response = subject.to_xml(), mimetype='application/xml')
