import sys
from datetime import datetime

from flask import Module, Response, request, session, g, \
                  render_template, redirect, url_for
from flaskext.wtf import Form, TextField, IntegerField, BooleanField, \
                         Required, NumberRange, URL
from sqlalchemy.orm import backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection

from concierge import db
from concierge.auth import User, requires_auth
from concierge.service_metadata_parser import serviceMetadataFromXML

from common import xml_kinds
from common import modelxmlserializer
from common.xmlserializer_parameters import SERIALIZER_PARAMETERS


services = Module(__name__, 'services')


service_favorites = db.Table('service_favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('service_id', db.Integer, db.ForeignKey('service.id')),
)


class ServiceRating(db.Model):
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'),
                           primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    rating = db.Column(db.Integer)

    service = db.relationship('Service', backref=backref('user_ratings',
        collection_class=attribute_mapped_collection('user')))
    user = db.relationship('User', backref=backref('service_ratings',
        collection_class=attribute_mapped_collection('service')))


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(xml_kinds.service_url(256), unique=True)
    name = db.Column(xml_kinds.service_name(256), unique=True)
    description = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', backref='services')
    users_favorite = db.relation('User', secondary=service_favorites,
                                 backref='favorite_services')
    rating_users = association_proxy('user_ratings', 'rating',
            creator=lambda u, r: ServiceRating(user=u, rating=r))

User.rating_services = association_proxy('service_ratings', 'rating',
        creator=lambda s, r: ServiceRating(service=s, rating=r))


class RegisterForm(Form):
    metadata_url = TextField('Metada URL', validators=[Required(),URL()])


class ServiceForm(Form):
    favorite = BooleanField('Favorite')
    rating = IntegerField('Rating', validators=[NumberRange(min=1, max=5)])


@services.route('/<id>/', methods=['GET', 'POST'])
@requires_auth
def service(id):
    user = g.user
    service = Service.query.get_or_404(id)
    form = ServiceForm(request.form)

    if form.validate_on_submit():
        if form.favorite.data and service not in user.favorite_services:
            user.favorite_services.append(service)
        elif not form.favorite.data and service in user.favorite_services:
            user.favorite_services.remove(service)
        user.rating_services[service] = form.rating.data
        db.session.commit()

        return redirect(url_for('service', id=id))

    form.favorite.data = service in user.favorite_services
    form.rating.data = user.rating_services.get(service)
    return render_template('service.html', service=service, form=form)


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


@services.route('/register/', methods=['GET','POST'])
@requires_auth
def register():
        form = RegisterForm(request.form)
        if form.validate_on_submit():
            url = form.metadata_url.data
            metadata = serviceMetadataFromXML(url)
            service = Service(name=metadata.name, url=url, active=True, user_id=session['id'])
            db.session.add(service)
            try:
                db.session.commit()
            except:
                db.session.rollback()
        return render_template('register_service.html', form=form)
    
@services.route('/favorites_list')
@requires_auth
def fav_list():
    user_id = session['id']
    user = User.query.get_or_404(user_id)
    favorites = user.favorite_services
    return render_template('favorite_list.html',favorites=favorites)
