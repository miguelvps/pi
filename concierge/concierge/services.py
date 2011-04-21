from flask import Module, render_template, request, Response
from concierge.auth import User
import sys
from concierge import db

sys.path.append('../../common/')
import xml_kinds
import modelxmlserializer
from xmlserializer_parameters import SERIALIZER_PARAMETERS


services = Module(__name__, 'services')



services_users = db.Table('services_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('service_id', db.Integer, db.ForeignKey('service.id')),
    db.Column('rating', db.Integer),
    db.Column('favorite', db.Boolean),
)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(xml_kinds.service_name(256), unique=True)
    url = db.Column(xml_kinds.service_url(256), unique=True)
    active= db.Boolean()
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    users = db.relationship('User', secondary=services_users, backref=db.backref('services', lazy='dynamic'))


    def __init__(self, name, url, user):
        self.name = name
        self.url = url
        self.active= True
        self.owner= user


@services.route('/', methods=['GET', 'POST'])
def service_list():
    services = Service.query.all()
    xml_text= modelxmlserializer.ModelList_xml(services).to_xml(SERIALIZER_PARAMETERS).toprettyxml()
    return Response(response=xml_text, mimetype="application/xml")


@services.route('/<id>', methods=['GET', 'DELETE'])
def service():
    if request.method=='GET':
        service = Service.query.get_or_404(id)
        xml_text= modelxmlserializer.Model_Serializer(service).to_xml(SERIALIZER_PARAMETERS).toprettyxml()
        return Response(response=xml_text, mimetype="application/xml")
    if request.method=='DELETE':
        return Response("not implemented yet. 5Y$WY%$")
