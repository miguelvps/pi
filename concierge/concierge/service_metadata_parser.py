from xml.dom.minidom import parse, parseString
import urllib2


def myGetElementsByTagName(xml_object, tagname, recursive=True):
    if recursive:
        return xml_object.getElementsByTagName(tagname)
    else:
        return [e for e in xml_object.childNodes if hasattr(e, 'tagName') and e.tagName== tagname]


class ServiceMetadataResourceMethod(object):
    GET, POST, PUT, DELETE, = range(4)
    method_dictionary= {'GET':GET, 'get':GET, 'POST':POST, 'post':POST, 'PUT':PUT, 'put':PUT, 'DELETE':DELETE, 'delete':DELETE, }
    QUERY, START, END= range(3)
    parameter_dictionary= {'QUERY':QUERY, 'query':QUERY, 'START':START, 'start':START, 'END':END, 'end':END}
    
    def __init__(self, xml_object, resource):
        self.resource= resource
        self.type, self.parameters= self.parse(xml_object)
        
    def parse(self, xml_object):
        '''returns method_type, parameters'''
        method_type_str= xml_object.attributes['type'].value
        method_type= self.method_dictionary[method_type_str]

        parameterlist_xml= xml_object.getElementsByTagName('parameter')
        parameters= [self.parameter_dictionary[p.childNodes[0].nodeValue] for p in parameterlist_xml]
        return method_type, parameters

class ServiceMetadataResource(object):
    def __init__(self, xml_object, parent_resource):
        self.parent= parent_resource
        self.url, self.keywords, self.methods, self.resources = self.parse(xml_object)

    def parse(self, xml_object):
        '''returns url, keywords, methods, subresources'''
        url= xml_object.attributes['url'].value
        if self.parent==None:
            assert url==""
        else:
            assert url!=""
        
        keywordslists_xml= xml_object.getElementsByTagName('keywords')
        assert 0<=len(keywordslists_xml)<=1
        if len(keywordslists_xml)==1:
            keywords_xml= keywordslists_xml[0].getElementsByTagName('keyword')
            keywords= [k.childNodes[0].nodeValue for k in keywords_xml]
        else:
            keywords=[]
        
        methodlist_xml= xml_object.getElementsByTagName('method') 
        methods= [ServiceMetadataResourceMethod(method, self) for method in methodlist_xml]
        
        resourcelist_xml= root_resources_xml= myGetElementsByTagName(xml_object,'resource', recursive=False)
        resources= [ServiceMetadataResource(r, self) for r in resourcelist_xml]

        return url, keywords, methods, resources

    def full_url():
        return parent.full_url()+self.url if self.parent else ""


class ServiceMetadata(object):
    XML,JSON= range(2)
    format_dictionary= {'XML':XML, 'xml':XML, 'JSON':JSON, 'json':JSON}
    def __init__(self, url):
        urlloader = urllib2.build_opener()
        page = urlloader.open(url).read()
        xml_object= parseString(page)
        self.name, self.url, self.description, self.formats, self.resource= self.parse(xml_object)

    def parse(self, xml_object):
        '''returns name, url, description, formats, resource'''
        services_xml= xml_object.getElementsByTagName('service')
        assert len(services_xml)==1
        service_xml= services_xml[0]

        name= service_xml.attributes['name'].childNodes[0].nodeValue
        url= service_xml.attributes['url'].childNodes[0].nodeValue
        
        descriptions_xml= service_xml.getElementsByTagName('description')
        assert 0<=len(descriptions_xml)<=1
        description= descriptions_xml[0].childNodes[0].nodeValue if len(descriptions_xml)==1 else ""

        formats_lists_xml= service_xml.getElementsByTagName('supported_formats')
        assert len(formats_lists_xml)==1
        formats_xml= formats_lists_xml[0].getElementsByTagName('format')
        formats= [self.format_dictionary[f.childNodes[0].nodeValue] for f in formats_xml]
        
        
        root_resources_xml= myGetElementsByTagName(service_xml,'resource', recursive=False)
        assert len(root_resources_xml)==1
        root_resource_xml= root_resources_xml[0]
        root_resource= ServiceMetadataResource(root_resource_xml, None)

        return name, url, description, formats, root_resource
    
    def global_search(self):
        '''returns the global search method'''
        MSRT= ServiceMetadataResourceMethod
        root_methods= self.resource.methods
        search_methods= filter(lambda m: m.type==MSRT.GET and MSRT.QUERY in m.parameters, root_methods)
        assert len(search_methods)==1
        return search_methods[0]
