import urllib2
from xml.etree import ElementTree
from concierge.services_models import *
from concierge import db
from common import rest_methods, rest_return_formats, rest_method_parameters

def xmlFromUrl(url):
    urlloader = urllib2.build_opener()
    page = urlloader.open(url).read()
    return ElementTree.fromstring(page)

def serviceMetadataFromXML(metadata_url):
    xml_object= xmlFromUrl(metadata_url)
    return parse_metadata(xml_object)



def parse_metadataResourceMethod(xml_object, parent_resource):
    '''returns method_type, parameters'''
    method_type_str= xml_object.get('type')
    method_type= getattr(rest_methods,method_type_str)
    parameterlist_xml= xml_object.findall('parameter')
    parameters= [ServiceMetadataResourceMethod_parameters(parameter=getattr(rest_method_parameters, p.text)) for p in parameterlist_xml]
    method= ServiceMetadataResourceMethod(parent_resource, method_type, parameters)
    db.session.add(method)
    return method

def parse_metadataResource(xml_object, parent_resource, service_object):
    '''returns url, keywords, methods, subresources'''
    url= xml_object.get('url')
    keywords_xml= xml_object.find('keywords')
    keywords= [ServiceMetadataResource_keywords(keyword=k.text)  for k in keywords_xml.getchildren()] if keywords_xml else []    
    resource= ServiceMetadataResource( parent_resource, service_object, url, keywords)
    resourcelist_xml= xml_object.findall('resource')
    child_resources= [parse_metadataResource(r, resource, service_object) for r in resourcelist_xml]
    resource.set_child_resources(child_resources)
    methodlist_xml= xml_object.findall('method') 
    methods= [parse_metadataResourceMethod(method, resource) for method in methodlist_xml]
    resource.set_methods(methods)
    db.session.add(resource)
    return resource

def parse_metadata(xml_object):
    '''returns name, url, description, formats, resource'''
    service_xml= xml_object
    assert service_xml.tag=='service'
    name= service_xml.get('name')
    url= service_xml.get('url')
    descriptions_xml= service_xml.find('description')
    description= descriptions_xml.text if descriptions_xml else ""
    formats_xml= service_xml.find('supported_formats')
    formats= [ServiceMetadata_formats(format=getattr(rest_return_formats, f.text)) for f in formats_xml.getchildren()]
    service_metadata= ServiceMetadata(name, url, description, formats, None)
    root_resource_xml= service_xml.find('resource')
    root_resource= parse_metadataResource(root_resource_xml, None, service_metadata)
    service_metadata.set_root_resource(root_resource)
    print "print 123",service_metadata.resources
    db.session.add(service_metadata)
    db.session.commit()
    return service_metadata
