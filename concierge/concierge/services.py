from flask import Module, render_template, request, Response, session
from concierge.auth import User
import sys
from concierge import db

sys.path.append('../../common/')
import xml_kinds
import modelxmlserializer
from xmlserializer_parameters import SERIALIZER_PARAMETERS


services = Module(__name__, 'services')

class Services_users_ratings(db.Model): 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), primary_key=True)
    rating = db.Column(db.Integer)

class Services_users_favorites(db.Model): 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), primary_key=True)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(xml_kinds.service_name(256), unique=True)
    url = db.Column(xml_kinds.service_url(256), unique=True)
    active= db.Boolean()
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, url, user):
        self.name = name
        self.url = url
        self.active= True
        self.owner= user

@services.route('/<id>/', methods=['GET', 'DELETE'])
def service(id):
    print id
    service = Service.query.get_or_404(id)
    return render_template('service.html', service = service) 

@services.route('/<service_id>/add_favorite',methods=['GET'])    
def add_bookmark(service_id):
    user_id = session['id']
    print Services_users_favorites.query.filter_by(Service_users_favorites.user_id == user_id, Service_users_favorites.service_id == service_id )
   
    return redirect('/')

        

@services.route('/api/', methods=['GET', 'POST'])
def service_list():
    services = Service.query.all()
    xml_text= modelxmlserializer.ModelList_xml(services).to_xml(SERIALIZER_PARAMETERS).toprettyxml()
    return Response(response=xml_text, mimetype="application/xml")


@services.route('/api/<id>', methods=['GET', 'DELETE'])
def service_xml(id):
    if request.method=='GET':
        service = Service.query.get_or_404(id)
        xml_text= modelxmlserializer.Model_Serializer(service).to_xml(SERIALIZER_PARAMETERS).toprettyxml()
        return Response(response=xml_text, mimetype="application/xml")
    if request.method=='DELETE':
        return Response("not implemented yet. 5Y$WY%$")
