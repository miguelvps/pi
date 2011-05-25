from flask import Module
from sqlalchemy.orm import backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

from datetime import datetime

from concierge import db
from concierge.auth import User, history_entry_services
from common import xml_kinds, rest_methods, rest_method_parameters

import urllib

services_models = Module(__name__, 'services')

#START OF SERVICE_USER MISC STUFF --------------------------------------

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

User.rating_services = association_proxy('service_ratings', 'rating',
        creator=lambda s, r: ServiceRating(service=s, rating=r))

#END OF SERVICE_USER MISC STUFF --------------------------------------


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    metadata_url = db.Column(xml_kinds.service_url(256), unique=True)
    url= db.Column(db.String)
    name = db.Column(xml_kinds.service_name(256), unique=True)
    description = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', backref='services')
    users_favorite = db.relation('User', secondary=service_favorites,
                                 backref='favorite_services')
                                 
    entries_service = db.relation('HistoryEntry', secondary=history_entry_services,
                                 backref='entry_services')
                                 
    rating_users = association_proxy('user_ratings', 'rating',
            creator=lambda u, r: ServiceRating(user=u, rating=r))

    formats = db.relationship('ServiceFormat', backref='service')
    resources = db.relationship('ServiceResource', backref='service')

    def global_search(self):
        '''returns the global search method'''

        filter_f= lambda m: m.type==rest_methods.GET and rest_method_parameters.QUERY in [p.parameter for p in m.parameters]
        search_methods= self.resources[0].find_methods( filter_function= filter_f)
        assert len(search_methods)==1
        return search_methods[0]

class ServiceFormat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    format = db.Column(db.Integer)


class ServiceResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('service_resource.id'))
    url = db.Column(db.String)

    keywords = db.relationship('ResourceKeyword', backref='resource')
    methods = db.relationship('ResourceMethod', backref='resource')
    resources = db.relationship('ServiceResource', backref=backref('parent', remote_side='ServiceResource.id'))

    def full_url(self):
        return self.parent.full_url()+self.url+"/" if self.parent else self.service.url

    def find_methods(self, recursive= False, filter_function= (lambda x: True) ):
        '''returns the methods of the resource and (optionally) subresources.
        Optionally filtered by a filter function (with the method as parameter).
        A call to resource.find_methods() with no parameters should give 
        a list equal to resource.methods'''
        methods= filter( filter_function, self.methods)
        if recursive:
            for subres in self.resources:
                methods.extend( subres.find_methods(recursive, filter_function))
        return methods

    def get_resource_by_url(self, url):
        if type(url)== str or type(url)==unicode:
            url= url.split('/')

        local_resource_name= url[0]
        local_resource= filter(lambda r:r.url==local_resource_name, self.resources)[0]
        if len(url)==1:
            return local_resource
        else:
            return local_resource.get_resource_by_url(url[1:])

    def get_parent_in_database(self):
        p= self.parent_id
        return ServiceResource.query.get(p) if p else None

class ResourceKeyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('service_resource.id'))
    keyword = db.Column(db.String)


class ResourceMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('service_resource.id'))
    type = db.Column(db.Integer)

    parameters = db.relationship('MethodParameter', backref="method")

    def execute(self, received_parameters):
        '''takes a dictionary of method parameters, executes the method
        and returns response'''
        if self.type!=rest_methods.GET:
            raise NotImplementedError("Can't execute a service method that is not a GET")
        method_url= self.resource.full_url()
        needed_parameters= [p.parameter for p in self.parameters]
        needed_parameters_names= [rest_method_parameters.reverse[p] for p in needed_parameters]
        #all received parameters must be method parameters
        assert all([r in needed_parameters for r in received_parameters.keys()])
        parameters_values= [received_parameters.get(p,'') for p in needed_parameters]
        parameters_kv= dict(zip(needed_parameters_names, parameters_values))
        params= urllib.urlencode(parameters_kv)
        page = urllib.urlopen(method_url + "?" + params).read().decode('utf-8')
        return page


class MethodParameter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method_id = db.Column(db.Integer, db.ForeignKey('resource_method.id'))
    parameter = db.Column(db.Integer)
