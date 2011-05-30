from flask import Module, request, session, render_template, Response, url_for
from concierge.services_models import Service

from common import xml_types, rest_method_parameters
from common.rest_method_parameters import START, END

service_browse = Module(__name__, 'service_browse')
start_end_parameters= sorted( [START, END] )

def method_is_listing( method ):
    return sorted(method.parameters) == start_end_parameters

def resource_list_method(resourse):
    ms= filter(lambda m: method_is_listing(m))
    return ms[0] if len(ms) else None

def url_for_resource(resource, service):
    if not resource: return "/"
    return url_for('browse', service_id=service.id)+'?resource='+resource.relative_url()

@service_browse.route('/services/<service_id>/browse/')
def browse(service_id):
    
    resource_url = request.args.get('resource', '')
    service = Service.query.get_or_404(service_id)
    if resource_url=='':
        resource= service.resources[0]  #root resource
    else:
        resource= service.resources[0].get_resource_by_url(resource_url)
    #import ipdb; ipdb.set_trace()
    return render_template('service_browse.html', resource=resource, service=service, url_for_resource=url_for_resource)

