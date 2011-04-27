import urllib2
from xml.etree import ElementTree

class ServiceMetadataResourceMethod(object):
    GET, POST, PUT, DELETE, = range(4)
    method_dictionary= {'GET':GET, 'get':GET, 'POST':POST, 'post':POST, 'PUT':PUT, 'put':PUT, 'DELETE':DELETE, 'delete':DELETE, }
    QUERY, START, END= 'query','start','end'
    parameter_dictionary= {'QUERY':QUERY, 'query':QUERY, 'START':START, 'start':START, 'END':END, 'end':END}
    
    def __init__(self, xml_object, resource):
        self.resource= resource
        self.type, self.parameters= self.parse(xml_object)
        
    def parse(self, xml_object):
        '''returns method_type, parameters'''
        method_type_str= xml_object.get('type')
        method_type= self.method_dictionary[method_type_str]

        parameterlist_xml= xml_object.findall('parameter')
        parameters= [self.parameter_dictionary[p.text] for p in parameterlist_xml]
        return method_type, parameters

    def execute(self, **args):
        '''takes a dictionary of method parameters, executes the method
        and returns response'''
        if self.type!=self.GET:
            raise NotImplementedError("Can't execute a service method that is not a GET")
        method_url= self.resource.full_url()
        received_parameters= args
        needed_parameters= self.parameters
        
        #all received parameters must be method parameters
        assert all([r in needed_parameters for r in received_parameters.keys()])
        parameters_values= [received_parameters.get(p,'') for p in needed_parameters]
        final_parameters= ["=".join(x) for x in zip(needed_parameters, parameters_values) ]
        call_url= method_url +  "?" + "&".join( final_parameters )
        urlloader = urllib2.build_opener()
        page = urlloader.open(call_url).read()
        page= page.decode('utf-8')
        return page
        
class ServiceMetadataResource(object):
    def __init__(self, xml_object, parent_resource, service_object):
        self.service= service_object
        self.parent= parent_resource
        self.url, self.keywords, self.methods, self.resources = self.parse(xml_object)

    def parse(self, xml_object):
        '''returns url, keywords, methods, subresources'''
        url= xml_object.get('url')
        if self.parent==None:
            assert url==""
        else:
            assert url!=""
        
        keywords_xml= xml_object.find('keywords')
        keywords= [k.text for k in keywords_xml.getchildren()] if keywords_xml else []
        
        methodlist_xml= xml_object.findall('method') 
        methods= [ServiceMetadataResourceMethod(method, self) for method in methodlist_xml]
        
        resourcelist_xml= xml_object.findall('resource')
        resources= [ServiceMetadataResource(r, self, self.service) for r in resourcelist_xml]
        
        return url, keywords, methods, resources
    
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
        

class ServiceMetadata(object):
    XML,JSON= range(2)
    format_dictionary= {'XML':XML, 'xml':XML, 'JSON':JSON, 'json':JSON}
    def __init__(self, url):
        urlloader = urllib2.build_opener()
        page = urlloader.open(url).read()
        xml_object= ElementTree.fromstring(page)
        self.name, self.url, self.description, self.formats, self.resource= self.parse(xml_object)

    def parse(self, xml_object):
        '''returns name, url, description, formats, resource'''
        service_xml= xml_object
        assert service_xml.tag=='service'

        name= service_xml.get('name')
        url= service_xml.get('url')
        
        descriptions_xml= service_xml.find('description')
        description= descriptions_xml.text if descriptions_xml else ""

        formats_xml= service_xml.find('supported_formats')
        formats= [f.text for f in formats_xml.getchildren()]
        
        root_resource_xml= service_xml.find('resource')
        root_resource= ServiceMetadataResource(root_resource_xml, None, self)

        return name, url, description, formats, root_resource
    
    def global_search(self):
        '''returns the global search method'''
        MSRT= ServiceMetadataResourceMethod
        filter_f= lambda m: m.type==MSRT.GET and MSRT.QUERY in m.parameters
        search_methods= self.resource.find_methods( filter_function= filter_f)
        assert len(search_methods)==1
        return search_methods[0]
