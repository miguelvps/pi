from xml.etree import ElementTree
from concierge.services_models import Service, ServiceFormat, ServiceResource, ResourceKeyword, ResourceMethod, MethodParameter
from common import rest_methods, rest_return_formats, rest_method_parameters


def parse_metadataResourceMethod(xml_object, parent_resource):
    '''returns method_type, parameters'''
    method_type_str= xml_object.get('type')
    method_type= getattr(rest_methods,method_type_str)
    parameterlist_xml= xml_object.findall('parameter')
    parameters= [MethodParameter(parameter=getattr(rest_method_parameters, p.text)) for p in parameterlist_xml]
    method= ResourceMethod(type=method_type, parameters=parameters)
    return method

def parse_metadataResource(xml_object):
    '''returns url, keywords, methods, subresources'''
    url= xml_object.get('url')
    keywords_xml= xml_object.find('keywords')
    keywords= [ResourceKeyword(keyword=k.text) for k in keywords_xml.getchildren()] if keywords_xml is not None else []
    resource= ServiceResource(url=url, keywords=keywords)
    resourcelist_xml= xml_object.findall('resource')
    resource.resources = [parse_metadataResource(resource_xml) for resource_xml in resourcelist_xml]
    methodlist_xml= xml_object.findall('method')
    resource.methods = [parse_metadataResourceMethod(method, resource) for method in methodlist_xml]
    return resource

def parse_metadata(xml):
    '''returns name, url, description, formats, resource'''
    service_xml = ElementTree.fromstring(xml)
    assert service_xml.tag=='service'
    name= service_xml.get('name')
    url= service_xml.get('url')
    assert url[-1]=="/" #convention 
    descriptions_xml= service_xml.find('description')
    description= descriptions_xml.text if descriptions_xml is not None else ""
    formats_xml= service_xml.find('supported_formats')
    formats= [ServiceFormat(format=getattr(rest_return_formats, f.text)) for f in formats_xml.getchildren()]
    root_resource_xml= service_xml.find('resource')
    root_resource= parse_metadataResource(root_resource_xml)
    service_metadata= Service(name=name, url=url, description=description, formats=formats, resources=[root_resource])
    return service_metadata
