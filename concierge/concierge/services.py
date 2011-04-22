from flask import Module, render_template, request, Response, session, redirect
from concierge.auth import User, requires_auth
import sys
from concierge import db
from flaskext.wtf import Form, TextField, PasswordField, Required, \
                         Length, EqualTo, ValidationError, IntegerField, BooleanField, NumberRange


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

class ServiceForm(Form):
    favorite = BooleanField('Favorite')
    rating = IntegerField('Rating', validators=[Required(),NumberRange(min=1, max=5)])
            
@services.route('/<service_id>/', methods=['GET', 'POST'])
def service(service_id):
    service = Service.query.get_or_404(service_id)
    user_id = session['id']
    favorite = Services_users_favorites.query.filter_by(user_id = user_id, service_id = service_id).first()
    favorite = bool(favorite)
    rating = Services_users_ratings.query.filter_by(user_id = user_id, service_id = service_id).first()
    rating = rating if rating else 0
    form = ServiceForm(request.form)
 

    
    if form.validate_on_submit():
        session.add(Services_users_ratings(user_id = user_id, service_id = service_id, rating = DEFAULT_RATING)))
        
        session.commit()
    
    
        form.favorite.data = favorite
        form.rating.data = rating

    return render_template('service.html', service = service, favorite = favorite, rating = rating, form=form  ) 

     
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
