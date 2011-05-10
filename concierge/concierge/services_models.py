from flask import Module
from sqlalchemy.orm import backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

from datetime import datetime

from concierge import db
from concierge.auth import User
from common import xml_kinds, rest_methods, rest_method_parameters

import urllib2
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
    service_metadata= db.relationship('ServiceMetadata', uselist=False)
    



#START OF METADATA TABLES ----------------------------------------------


class ServiceMetadataResourceMethod_parameters(db.Model):
    method_id= db.Column(db.Integer, db.ForeignKey('service_metadata_resource_method.id'), primary_key=True)
    parameter=  db.Column(db.Integer, primary_key= True)


class ServiceMetadataResourceMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_id= db.Column(db.Integer, db.ForeignKey('service_metadata_resource.id'))
    type= db.Column(db.Integer)
    parameters= db.relationship('ServiceMetadataResourceMethod_parameters')
    
    def __init__(self, resource, type, parameters):
        self.resource, self.type, self.parameters= resource, type, parameters

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
        final_parameters= ["=".join(x) for x in zip(needed_parameters_names, parameters_values) ]
        call_url= method_url +  "?" + "&".join( final_parameters )
        urlloader = urllib2.build_opener()
        page = urlloader.open(call_url).read()
        page= page.decode('utf-8')
        return page

class ServiceMetadataResource_keywords(db.Model):
     resource_id= db.Column(db.Integer, db.ForeignKey('service_metadata_resource.id'), primary_key=True)
     keyword = db.Column(db.String, primary_key=True)


class ServiceMetadataResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id= db.Column(db.Integer, db.ForeignKey('service_metadata.id'))
    parent_id= db.Column(db.Integer, db.ForeignKey('service_metadata_resource.id'))
    url= db.Column(db.String)
    keywords= db.relationship('ServiceMetadataResource_keywords')
    methods= db.relationship('ServiceMetadataResourceMethod', backref="resource")
    resources= db.relationship('ServiceMetadataResource', backref=backref('parent', remote_side='ServiceMetadataResource.id'))
    
    
    def __init__(self, parent, service_object, url, keywords, methods=[], child_resources=[]):
        self.service, self.parent= service_object, parent
        self.url, self.keywords, self.methods, self.resources = url, keywords, methods, child_resources

    def set_child_resources(self, child_resources):
        self.resources= child_resources

    def set_methods(self, methods):
        self.methods=methods
        
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
        
class ServiceMetadata_formats(db.Model):
    service_id= db.Column(db.Integer, db.ForeignKey('service_metadata.id'), primary_key=True)
    format=  db.Column(db.Integer, primary_key=True)

class ServiceMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id= db.Column(db.Integer, db.ForeignKey('service.id'))
    name= db.Column(db.String)
    url= db.Column(db.String)
    description= db.Column(db.String)
    formats= db.relationship('ServiceMetadata_formats')
    resources= db.relationship('ServiceMetadataResource', backref='service')
    
    def __init__(self, name, url, description, formats, root_resource=None):
        self.name, self.url, self.description, self.formats, self.resource= name, url, description, formats, root_resource
        
    def global_search(self):
        '''returns the global search method'''
        
        filter_f= lambda m: m.type==rest_methods.GET and rest_method_parameters.QUERY in [p.parameter for p in m.parameters]
        search_methods= self.resources[0].find_methods( filter_function= filter_f)
        assert len(search_methods)==1
        return search_methods[0]

    def set_root_resource(self, root_resource):
        self.resources= [root_resource]

#END OF METADATA TABLES ------------------------------------------------





