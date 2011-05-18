from flask import Flask, Response
from flaskext.sqlalchemy import SQLAlchemy
from common import xml_kinds
from common import modelxmlserializer
from common.xmlserializer_parameters import SERIALIZER_PARAMETERS


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

    courses =  db.relationship('Course', backref='department')

xml_kinds.set_model_kind(Department, xml_kinds.department)


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

xml_kinds.set_model_kind(Course, xml_kinds.course)


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

xml_kinds.set_model_kind(Subject, xml_kinds.subject)


@app.route('/')
def search():
    pass

@app.route('/departments')
def departments():
    departments = Department.query.all()
    xml_text= modelxmlserializer.ModelList_xml(departments).to_xml(SERIALIZER_PARAMETERS).toxml()
    return Response(xml_text, mimetype='application/xml')

@app.route('/department/<id>')
def department(id):
    department = Department.query.get_or_404(id)
    xml_text= modelxmlserializer.Model_Serializer(department).to_xml(SERIALIZER_PARAMETERS).toprettyxml()
    return Response(xml_text, mimetype='application/xml')

@app.route('/courses')
def courses():
    courses = Course.query.all()
    xml_text= modelxmlserializer.ModelList_xml(courses).to_xml(SERIALIZER_PARAMETERS).toxml()
    return Response(xml_text, mimetype='application/xml')

@app.route('/courses/<id>')
def course(id):
    course = Course.query.get_or_404(id)
    xml_text= modelxmlserializer.Model_Serializer(course).to_xml(SERIALIZER_PARAMETERS).toprettyxml()
    return Response(xml_text, mimetype='application/xml')

@app.route('/subjects')
def subjects():
    subjects = Subject.query.all()
    xml_text= modelxmlserializer.ModelList_xml(subjects).to_xml(SERIALIZER_PARAMETERS).toxml()
    return Response(xml_text, mimetype='application/xml')

@app.route('/subjects/<id>')
def subject(id):
    subject = Subject.query.get_or_404(id)
    xml_text= modelxmlserializer.Model_Serializer(subject).to_xml(SERIALIZER_PARAMETERS).toprettyxml()
    return Response(xml_text, mimetype='application/xml')
