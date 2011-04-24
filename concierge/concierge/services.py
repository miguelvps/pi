import sys
from datetime import datetime

from flask import Module, Response, request, session, render_template, redirect
from flaskext.wtf import Form, TextField, IntegerField, BooleanField, \
                         Required, NumberRange, URL
from sqlalchemy.orm import backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection

from concierge import db
from concierge.auth import User, requires_auth
from concierge.service_metadata_parser import ServiceMetadata

sys.path.append('../../common/')
import xml_kinds
import modelxmlserializer
from xmlserializer_parameters import SERIALIZER_PARAMETERS


services = Module(__name__, 'services')


class ServiceFavorite(db.Model):
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'),
                           primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    service = db.relationship('Service', backref='user_favorites')
    user = db.relationship('User', backref='service_favorites')


class ServiceRating(db.Model):
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'),
                           primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    rating = db.Column(db.Integer)

    service = db.relationship('Service', backref=backref('user_ratings',
        collection_class=attribute_mapped_collection('service')))
    user = db.relationship('User', backref=backref('service_ratings',
        collection_class=attribute_mapped_collection('user')))


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(xml_kinds.service_url(256), unique=True)
    name = db.Column(xml_kinds.service_name(256), unique=True)
    description = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', backref='services')
    favorite_users = association_proxy('user_favorites', 'user',
            creator=lambda u: ServiceFavorite(user=u))
    rating_users = association_proxy('user_ratings', 'rating',
            creator=lambda u, r: ServiceRating(user=u, rating=r))

User.favorite_services = association_proxy('service_favorites', 'service',
        creator=lambda s: ServiceFavorite(service=s))
User.rating_services = association_proxy('service_ratings', 'rating',
        creator=lambda s, r: ServiceRating(service=s, rating=r))


class RegisterForm(Form):
    metadata_url = TextField('Metada URL', validators=[Required(),URL()])


class ServiceForm(Form):
    favorite = BooleanField('Favorite')
    rating = IntegerField('Rating', validators=[NumberRange(min=1, max=5)])


@services.route('/<service_id>/', methods=['GET', 'POST'])
@requires_auth
def service(service_id):
    service = Service.query.get_or_404(service_id)
    user_id = session['id']
    favorite = ServiceFavorite.query.filter_by(user_id=user_id, service_id=service_id).first()
    rating = ServiceRating.query.filter_by(user_id=user_id, service_id=service_id).first()
    rating = rating.rating if rating else 0
    form = ServiceForm(request.form)

    if form.validate_on_submit():
        if form.favorite.data and not favorite :
            db.session.add(ServiceFavorite(user_id=user_id, service_id=service_id))
        elif not form.favorite.data and favorite:
            db.session.delete(favorite)
        db.session.merge(ServiceRating(user_id=user_id, service_id=service_id, rating=form.rating.data))
        db.session.commit()
        return redirect('/services/%s' %service_id)

    form.favorite.data = bool(favorite)
    form.rating.data = rating
    return render_template('service.html', service = service, form=form  )


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
            metadata = ServiceMetadata(url)
            service = Service(name=metadata.name, url=metadata.url, active=True, user_id=session['id'])
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
