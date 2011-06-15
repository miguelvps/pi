import urllib
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from xml.etree import ElementTree
try: from xml.etree.ElementTree import ParseError
except:
    from xml.parsers.expat import ExpatError
    ParseError = ExpatError
from flask import Module, request, g, render_template, redirect, url_for, flash
from flaskext.wtf import Form, TextField, IntegerField, BooleanField, \
                         Required, NumberRange, URL, ValidationError
from concierge import db
from concierge.auth import requires_auth
from concierge.services_models import Service, ResourceMethod
from concierge.service_metadata_parser import parse_metadata
from concierge import xml_to_html
from common import rest_methods, rest_method_parameters

RESULTS_PER_PAGINATED_PAGE= 15

services = Module(__name__, 'services')


@services.before_app_request
def before_request():
    if request.cookies.get('online'):
        if hasattr(g, 'user'):
            last_seen = g.user.last_seen
            services = Service.query.filter(Service.created > last_seen).all()
            for service in services:
                flash('New service: %s' % service.name, 'info')
            g.user.last_seen = datetime.utcnow()
            db.session.add(g.user)
            db.session.commit()


class RegisterForm(Form):
    url = TextField('Metada URL', validators=[Required(), URL()])

    def validate_metadata_url(form, field):
        if Service.query.filter_by(url=form.metadata_url.data).first():
            raise ValidationError('This service is already registered')


class ServiceForm(Form):
    favorite = BooleanField('Favorite')
    rating = IntegerField('Rating', validators=[NumberRange(min=1, max=5)])


@services.route('/<id>', methods=['GET', 'POST'])
def service(id):
    user = getattr(g, 'user', None)
    service = Service.query.get_or_404(id)
    form = ServiceForm(request.form)

    if user:
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


@services.route('/register', methods=['GET','POST'])
@requires_auth
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        url = form.url.data
        try:
            metadata = urllib.urlopen(url).read()
            service = parse_metadata(metadata)
            service.metadata_url = url
            service.user = g.user
            db.session.add(service)
            db.session.commit()
            return redirect('/')
        except IOError:
            form.url.errors.append("Unable to fetch the metadata file")
        except ParseError:
            form.url.errors.append("Metadata file not well-formed")
        except IntegrityError:
            form.url.errors.append("Invalid metadata info, already registered ?")
            db.session.rollback()
    return render_template('register_service.html', form=form)


@services.route('/favorites')
def favorites():
    if hasattr(g, 'user'):
        user = g.user
        favorites = user.favorite_services
        return render_template('favorites.html',favorites=favorites)
    return render_template('favorites.html', favorites=[])


@services.route('/ratings')
def ratings():
    if hasattr(g, 'user'):
        user = g.user
        ratings = user.rating_services
        return render_template('ratings.html', ratings=ratings)
    return render_template('ratings.html', ratings={})


# /import?f=1&f=2&r=2.1
@services.route('/import')
@requires_auth
def imports():
    user = g.user
    favorites = set(request.args.getlist('f'))
    ratings = set([tuple(r.split('.')) for r in request.args.getlist('r')])

    for f in favorites:
        service = Service.query.get(f)
        if (service and service not in user.favorite_services):
            user.favorite_services.append(service)

    for r in ratings:
        service = Service.query.get(r[0])
        if (service):
            user.rating_services[service] = r[1]

    db.session.add(user)
    db.session.commit()
    return redirect("/")







@services.route('/<id>/browse')
def browse(id):
    service = Service.query.get_or_404(id)
    root = service.resources[0]
    resources = []
    for resource in root.resources:
        if filter(lambda m: m.type==rest_methods.GET, resource.methods):
            resources.append(resource)
    return render_template('service_browse.html', resources=resources, service=service)

def complete_method_args(method, given_args, add_start_end=False):
    '''given a method, verifies it's parameters and takes their values
    from dictionary given_args'''
    START, END, QUERY, LATLNG= rest_method_parameters.START, rest_method_parameters.END,  rest_method_parameters.QUERY,rest_method_parameters.LATLNG
    results= {}
    method_parameters= [p.parameter for p in method.parameters]
    for parameter in method_parameters:
        param_name= rest_method_parameters.reverse[parameter]
        value= given_args.get(param_name)
        if not value and parameter==START and add_start_end:
            value=0
        if not value and parameter==END and add_start_end:
            value=RESULTS_PER_PAGINATED_PAGE
        results[parameter]=value
    return results
    
    
    
def browse_resource_unpaginated(url, service, method):
    xml= method.execute({}, url_override=service.url+url)
    element = ElementTree.fromstring(xml)
    html= xml_to_html.render(element)
    return render_template('service_browse_resource.html', c="page-map" if element.get('type') == "map" else "", service=service, html=html, url=url)


def browse_resource_paginated(url, service, method, args):
    args= complete_method_args(method, args, add_start_end=True)
    xml= method.execute(args)
    html= xml_to_html.render(ElementTree.fromstring(xml))
    n= RESULTS_PER_PAGINATED_PAGE
    if args[rest_method_parameters.END]==n:
        #first page
        html+= '''
        <script>
        var doing_request= false;
        var start= %i;
        var url= "%s";
        $(document).bind('scrollstop',function()
            {
            var x= $('body').height() +$(document).scrollTop() ;
            var y= $(document).height();
            if ((x>=y) && (!doing_request))
                    {
                    doing_request= true;
                    $.ajax({url: url+"?start="+start+"&end="+(start+%i), success:
                    function (data)
                        {
                        start+=%i;
                        $("ul.list").append(data);
                        $("ul.list").listview("refresh");
                        doing_request= false;
                        } });
                    
                    }
            });

        </script>'''%(n, "/services/"+str(service.id)+"/browse/"+url, n, n )
        return render_template('service_browse_resource.html', service=service, html=html, url=url)
    else:
        #not first page, don't return all the page, only li elements
        html_tree= ElementTree.fromstring(html.encode('utf-8'))
        assert html_tree.tag=="ul"
        html= "".join(map(ElementTree.tostring, html_tree.getchildren() ))
        return html
            
@services.route('/<id>/browse/<path:url>')
def browse_resource(id, url):
    def paginated_method(method):
        parameters= [p.parameter for p in method.parameters]
        return all([p in parameters for p in (START, END)])
    START, END, GET= rest_method_parameters.START, rest_method_parameters.END, rest_methods.GET

    service = Service.query.get_or_404(id)
    root = service.resources[0]
    resource = root.get_resource_by_url(url)
    methods= filter(lambda m: m.type==GET, resource.methods)
    assert len(methods) #resourse must have at least one GET method
    paginated= filter(paginated_method, methods)
    args= request.args
    if len(paginated):
        return browse_resource_paginated(url, service, paginated[0], request.args) #choose first paginated method
    else:
        return browse_resource_unpaginated(url, service, methods[0]) #choose any GET method
