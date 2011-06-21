import urllib
from functools import wraps
from flask import Module, request, session, g, abort, jsonify
from werkzeug import generate_password_hash

from concierge import db
from concierge.auth import User, HistoryEntry
from concierge.services_models import Service, ServiceRating
from concierge.service_metadata_parser import parse_metadata
from concierge.common import rest_methods


api = Module(__name__, 'api')

def requires_api_auth(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not session.get('auth') and not hasattr(g, 'user'):
            return abort(401)
        return f(*args, **kwargs)
    return decorator

@api.route('/search')
def search():
    """ Search on all services """
    services = Service.query.all()
    data = []
    for service in services:
        method = service.global_search()
        url = method.resource.absolute_url()
        if request.args:
            url += "?" + urllib.urlencode(request.args)
        data.append({'id': service.id,
                     'name': service.name,
                     'data': urllib.urlopen(url).read()})
    return jsonify(data=data)

@api.route('/services')
def services():
    """ List all services """
    services = Service.query.all()
    return jsonify(services=[{'id': s.id, 'name': s.name} for s in services])

@api.route('/services', methods=['POST'])
@requires_api_auth
def service_create():
    """ Create a service """
    user = g.user
    url = request.json['url']
    try:
        metadata = urllib.urlopen(url).read()
        service = parse_metadata(metadata)
        service.metadata_url = url
        service.user = user
        db.session.add(service)
        db.session.commit()
        return ""
    except:
        return abort(400)

@api.route('/services/<id>')
def service(id):
    """ Get info about a service """
    service = Service.query.get_or_404(id)
    return jsonify(id=service.id,
                   name=service.name,
                   description=service.description,
                   created=str(service.created),
                   active=service.active)

@api.route('/services/<id>', methods=['DELETE', 'PUT'])
@requires_api_auth
def service_manage(id):
    """ Delete or update a service """
    user = g.user
    service = Service.query.get_or_404(id)
    if service.user_id != user.id:
        return abort(403)
    if request.method == 'DELETE':
        service.delete()
    if request.method == 'PUT':
        raise Exception('Not implemented')
    return ""

@api.route('/services/<id>/search')
def service_search(id):
    service = Service.query.get_or_404(id)
    method = service.global_search()
    url = method.resource.absolute_url()
    if request.args:
        url += "?" + urllib.urlencode(request.args)
    data = urllib.urlopen(url).read()
    return jsonify(data=data)

@api.route('/services/<id>/browse')
def service_browse(id):
    """ Browses the top level resources of a service """
    service = Service.query.get_or_404(id)
    root = service.resources[0]
    resources = []
    for resource in root.resources:
        if filter(lambda m: m.type==rest_methods.GET, resource.methods):
            resources.append(resource)
    return jsonify(resources=[{'name':resource.url, 'url':request.base_url+"/"+resource.url} for resource in resources])

@api.route('/services/<id>/browse/<path:url>')
def service_browse_resource(id, url):
    """ Browses a resource in a service """
    service = Service.query.get_or_404(id)
    root = service.resources[0]
    resource = root.get_resource_by_url(url)
    methods= filter(lambda m: m.type==rest_methods.GET, resource.methods)
    assert len(methods) #resourse must have at least one GET method
    url = service.url+url
    if request.args:
        url += "?" + urllib.urlencode(request.args)
    data = urllib.urlopen(url).read()
    return jsonify(data=data)

@api.route('/users')
def users():
    """ List all users """
    users = User.query.all()
    return jsonify(users=[{'id': s.id, 'username': s.username} for s in users])

@api.route('/users', methods=['POST'])
def user_create():
    print request.json
    """ Create a user """
    user = User(username=request.json['username'],
                password=generate_password_hash(request.json['password']))
    db.session.add(user)
    db.session.commit()
    return jsonify(id=user.id,
                    username=user.username,
                    created=str(user.created),
                    last_seen=str(user.last_seen))

@api.route('/users/<id>')
def user(id):
    """ Get info about a user """
    user = User.query.get_or_404(id)
    return jsonify(id=user.id,
                    username=user.username,
                    created=str(user.created),
                    last_seen=str(user.last_seen))

@api.route('/users/<id>/ratings', methods=['GET', 'POST'])
@requires_api_auth
def user_ratings(id):
    """ Get user ratings or add a rating """
    user = g.user
    if user.id != id:
        return abort(403)
    if request.method == 'GET':
        return jsonify(ratings=[{'id': service.id, 'name': service.name, 'rating': rating} for service, rating in user.rating_services.items()])
    if request.method == 'POST':
        service = Service.query.get_or_404(request.json['id'])
        rating = request.json['rating']
        user.rating_services[service] = rating
        return ""

@api.route('/users/<user_id>/ratings/<service_id>', methods=['DELETE', 'PUT'])
@requires_api_auth
def user_rating(user_id, service_id):
    """ Delete or update a rating """
    user = g.user
    if user.id != user_id:
        return abort(403)
    sr = ServiceRating.query.filter_by(user=user, service_id=service_id).get_or_404()
    if request.method == 'DELETE':
        sr.delete()
    if request.method == 'PUT':
        sr.rating = request.json['rating']
    return ""

@api.route('/users/<id>/favorites', methods=['GET', 'POST'])
@requires_api_auth
def user_favorites(id):
    """ Get user favorites or add a favorite """
    user = g.user
    if user.id != id:
        return abort(403)
    if request.method == 'GET':
        return jsonify(favorites=[{'id': service.id, "name": service.name} for service in user.favorite_services])
    if request.method == 'POST':
        service = Service.query.get_or_404(request.json['id'])
        if service not in user.favorite_service:
            user.favorite_services.append(service)
            return ""
        return abort(404)

@api.route('/users/<user_id>/favorite/<service_id>', methods=['DELETE'])
@requires_api_auth
def user_favorite(user_id, service_id):
    """ Remove a favorite """
    user = g.user
    if user.id != user_id:
        return abort(403)
    for service in user.favorite_services:
        if service.id == service_id:
            service.delete()
            return ""
    return abort(404)

@api.route('/users/<id>/history', methods=['GET', 'DELETE'])
@requires_api_auth
def user_history(id):
    """ Get or clear user history """
    user = g.user
    if user.id != id:
        return abort(403)
    if request.method == 'GET':
        history = HistoryEntry.query.filter_by(user=user).all()
        return jsonify(history=[{'created': str(h.created), 'query': h.search_query} for h in history])
    if request.method == 'DELETE':
        HistoryEntry.query.filter_by(id=id, user=user).delete()
        return ""
