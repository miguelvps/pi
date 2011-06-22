import urllib
from functools import wraps
from flask import Module, request, session, g, abort, jsonify

from concierge import db
from concierge.auth import User, HistoryEntry
from concierge.services_models import Service, ServiceRating
from concierge.service_metadata_parser import parse_metadata
from concierge.common import rest_methods


api = Module(__name__, 'api')

@api.before_request
def before_request():
    """ Authenticates the user on request """
    if request.authorization:
        user = User.query.filter_by(username=request.authorization.username).first()
        if user and user.check_password(request.authorization.password):
            g.user = user

def requires_api_auth(f):
    """ Requires authentication decorator """
    @wraps(f)
    def decorator(*args, **kwargs):
        if not hasattr(g, 'user'):
            return abort(401)
        return f(*args, **kwargs)
    return decorator

@api.route('/search')
def search():
    """ Search on all services """
    services = Service.query.all()
    query = request.args.get('query')
    data = []
    if hasattr(g, 'user'):
        db.session.add(HistoryEntry(user=g.user, search_query=query, entry_services=services))
        db.session.commit()
    for service in services:
        method = service.global_search()
        url = method.resource.absolute_url()
        if request.args:
            url += "?" + urllib.urlencode(request.args)
        result = urllib.urlopen(url).read()
        if result:
            data.append({'id': service.id,
                         'name': service.name,
                         'data': result})
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

@api.route('/services/<int:id>')
def service(id):
    """ Get info about a service """
    service = Service.query.get_or_404(id)
    return jsonify(id=service.id,
                   name=service.name,
                   description=service.description,
                   created=str(service.created),
                   active=service.active)

@api.route('/services/<int:id>', methods=['DELETE', 'PUT'])
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

@api.route('/services/<int:id>/search')
def service_search(id):
    """ Search on a specific service """
    service = Service.query.get_or_404(id)
    query = request.args.get('query')
    if hasattr(g, 'user'):
        db.session.add(HistoryEntry(user=g.user, search_query=query, entry_services=[service]))
        db.session.commit()
    method = service.global_search()
    url = method.resource.absolute_url()
    if request.args:
        url += "?" + urllib.urlencode(request.args)
    data = urllib.urlopen(url).read()
    return jsonify(data=data)

@api.route('/services/<int:id>/browse')
def service_browse(id):
    """ Browses the top level resources of a service """
    service = Service.query.get_or_404(id)
    root = service.resources[0]
    resources = []
    for resource in root.resources:
        if filter(lambda m: m.type==rest_methods.GET, resource.methods):
            resources.append(resource)
    return jsonify(resources=[{'name':resource.url, 'url':request.base_url+"/"+resource.url} for resource in resources])

@api.route('/services/<int:id>/browse/<path:url>')
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
    """ Create a user """
    print request.json['username']
    print request.json['password']
    user = User(request.json['username'], request.json['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify(id=user.id,
                    username=user.username,
                    created=str(user.created),
                    last_seen=str(user.last_seen))

@api.route('/users/<int:id>')
def user(id):
    """ Get info about a user """
    user = User.query.get_or_404(id)
    return jsonify(id=user.id,
                    username=user.username,
                    created=str(user.created),
                    last_seen=str(user.last_seen))

@api.route('/users/login', methods=['POST'])
def login():
    """ Authenticate a user, session based """
    user = User.query.filter_by(username=request.json['username']).first()
    if not user:
        return abort(404)
    if user.check_password(request.json['password']):
        g.user = user
        session['id'] = user.id
        session['username'] = user.username
        session['auth'] = True
        session.permanent = request.json.get('permanent')
        return ""
    return abort(401)

@api.route('/users/logout')
@requires_api_auth
def logout():
    """ Logout a user, session based """
    session.pop('auth')
    return ""

@api.route('/users/<int:id>/ratings', methods=['GET', 'POST'])
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

@api.route('/users/<int:user_id>/ratings/<int:service_id>', methods=['DELETE', 'PUT'])
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

@api.route('/users/<int:id>/favorites', methods=['GET', 'POST'])
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

@api.route('/users/<int:user_id>/favorites/<int:service_id>', methods=['DELETE'])
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

@api.route('/users/<int:id>/history', methods=['GET', 'DELETE'])
@requires_api_auth
def user_history(id):
    """ Get or clear user history """
    user = g.user
    if user.id != id:
        return abort(403)
    if request.method == 'GET':
        history = HistoryEntry.query.filter_by(user=user).all()
        return jsonify(history=[{'created': str(h.created),
                                 'query': h.search_query,
                                 'services': [{'id':s.id, 'name':s.name} for s in h.entry_services]}
                                for h in history])
    if request.method == 'DELETE':
        HistoryEntry.query.filter_by(user=user).delete()
        return ""
