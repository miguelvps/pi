import re
import urllib
from datetime import datetime

from flask import Module
from flaskext.babel import get_locale
from sqlalchemy.orm import backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

from concierge import db
from concierge.auth import User, history_entry_services
from common import rest_methods, rest_method_parameters


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
    metadata_url = db.Column(db.String(256), unique=True)
    url= db.Column(db.String)
    name = db.Column(db.String(256), unique=True)
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
        filter_f= lambda m: m.type==rest_methods.GET and ( rest_method_parameters.QUERY in [p.parameter for p in m.parameters] \
            or rest_method_parameters.NOME in [p.parameter for p in m.parameters] ) #G07 search
        search_methods= self.resources[0].find_methods(filter_function= filter_f, recursive=True)
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

    def relative_url(self, add_service_url=False):
        if not self.parent:
            return (self.service.url[:-1]) if add_service_url else ""
        else:
            return self.parent.relative_url(add_service_url=add_service_url)+"/"+self.url

    def absolute_url(self):
        return self.relative_url(add_service_url=True)

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
        if isinstance(url, str) or isinstance(url, unicode):
            url = url.split('/')
        rn = url[0]  #local resource name
        r = filter(lambda r:re.match(r.url, rn), self.resources)[0] if rn else self
        return r if len(url) == 1 else r.get_resource_by_url(url[1:])


class ResourceKeyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('service_resource.id'))
    keyword = db.Column(db.String)


class ResourceMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('service_resource.id'))
    type = db.Column(db.Integer)

    parameters = db.relationship('MethodParameter', backref="method")

    def execute(self, received_parameters, url_override="", locale=None):
        '''takes a dictionary of method parameters, executes the method
        and returns response'''
        if self.type!=rest_methods.GET:
            raise NotImplementedError("Can't execute a service method that is not a GET")
        method_url= url_override if url_override else self.resource.absolute_url()
        needed_parameters= dict([(p.parameter, rest_method_parameters.reverse[p.parameter]) for p in self.parameters])
        #all received parameters must be method parameters
        #assert all([r in needed_parameters for r in received_parameters.keys()])
        parameters_kv= dict([(needed_parameters.get(k) or k, v) for k,v in received_parameters.items()])
        for k,v in parameters_kv.items():
            if isinstance(v, unicode):
                parameters_kv[k] = v.encode('utf-8')
        locale = locale or get_locale()
        if locale:
            parameters_kv['lang'] = locale
        params= urllib.urlencode(parameters_kv)
        try:
            page = urllib.urlopen(method_url + "?" + params) #
        except:
            return '<entity type="list"/>'
        page = page.read()
        return page

    @staticmethod
    def execute_several(method_parameters_pairs, thread_number=8, locale=None):
        '''
        See execute().
        given a list of tuples in the form (method, parameters),
        executes the given methods in parallel (threaded), and returns a
        list of results (in the same order).
        Does not throw exceptions; if any of the methods fails, its
        result is None.'''
        from Queue import Queue
        import threading
        tasks_queue = Queue()
        results_list = [0]*len(method_parameters_pairs)

        class ExecuteThread(threading.Thread):
            def __init__(self, tasks_queue, results_list):
                threading.Thread.__init__(self)
                self.tasks_queue = tasks_queue
                self.results_list= results_list

            def run(self):
                while True:
                    #n is the desired position of the result in the
                    #results_list (technique like Schwartzian transform)
                    n, x = self.tasks_queue.get()
                    method, parameters= x
                    try:
                        result= method.execute(parameters, locale=locale)
                    except IOError:
                        #communication error
                        result= None
                    # print "set", n, "...",result
                    result = result or None
                    self.results_list[n]= result
                    self.tasks_queue.task_done()

        for i in range(thread_number):
            t = ExecuteThread(tasks_queue, results_list)
            t.setDaemon(True)
            t.start()

        decorated= [(i, pair) for i,pair in enumerate(method_parameters_pairs)]
        map(tasks_queue.put, decorated)
        #wait until everything has been processed     
        tasks_queue.join()
        return results_list



class MethodParameter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method_id = db.Column(db.Integer, db.ForeignKey('resource_method.id'))
    parameter = db.Column(db.Integer)
