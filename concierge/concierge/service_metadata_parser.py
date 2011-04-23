example_metadata='''
    <service name="pessoas" url="http://concierge.dyndns.org/services/pessoas">
    <description> Este servico guarda informacao dos docentes</description>
    <supported_formats>
        <format>xml</format>
    </supported_formats>

    <resource url="">
        <keywords>
            <keyword>docente</keyword>
            <keyword>docentes</keyword>
            <keyword>professor</keyword>
            <keyword>professores</keyword>
        </keywords>
        <method type="GET" >
            <parameter>query</parameter> 
        </method>
        <resource url="pessoas">
            <method type="GET" >
                <parameter>start</parameter>
                <parameter>end</parameter> 
            </method>
        </resource >
    </resource>
</service>
'''

def myGetElementsByTagName(xml_object, tagname, recursive=True):
    if recursive:
        return xml_object.getElementsByTagName(tagname)
    else:
        return [e for e in xml_object.childNodes if hasattr(e, 'tagName') and e.tagName== tagname]


from xml.dom.minidom import parse, parseString
import urllib2
class ServiceMetadataResourceMethod(object):
    GET, POST, PUT, DELETE, = range(4)
    method_dictionary= {'GET':GET, 'get':GET, 'POST':POST, 'post':POST, 'PUT':PUT, 'put':PUT, 'DELETE':DELETE, 'delete':DELETE, }
    QUERY, START, END= range(3)
    parameter_dictionary= {'QUERY':QUERY, 'query':QUERY, 'START':START, 'start':START, 'END':END, 'end':END}
    
    def __init__(self, xml_object):
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
        self.keywords, self.methods, self.resources = self.parse(xml_object)

    def parse(self, xml_object):
        '''returns keywords, methods, subresources'''
        if self.parent==None:
            assert xml_object.attributes['url'].value==""
        else:
            assert xml_object.attributes['url'].value!=""
        
        keywordslists_xml= xml_object.getElementsByTagName('keywords')
        assert 0<=len(keywordslists_xml)<=1
        if len(keywordslists_xml)==1:
            keywords_xml= keywordslists_xml[0].getElementsByTagName('keyword')
            keywords= [k.childNodes[0].nodeValue for k in keywords_xml]
        else:
            keywords=[]
        
        methodlist_xml= xml_object.getElementsByTagName('method') 
        methods= [ServiceMetadataResourceMethod(method) for method in methodlist_xml]
        
        resourcelist_xml= root_resources_xml= myGetElementsByTagName(xml_object,'resource', recursive=False)
        resources= [ServiceMetadataResource(r, self) for r in resourcelist_xml]

        return keywords, methods, resources

        

class ServiceMetadata(object):
    XML,JSON= range(2)
    format_dictionary= {'XML':XML, 'xml':XML, 'JSON':JSON, 'json':JSON}
    def __init__(self, url):
        urlloader = urllib2.build_opener()
        page = urlloader.open(url).read()
        xml_object= parseString(page)
        self.description, self.formats, self.resource= self.parse(xml_object)

    def parse(self, xml_object):
        '''returns description, formats, resource'''
        services_xml= xml_object.getElementsByTagName('service')
        assert len(services_xml)==1
        service_xml= services_xml[0]
        
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

        return description, formats, root_resource
