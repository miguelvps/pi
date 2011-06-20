from common.awesomexml import AwesomeXml
from xml.etree import ElementTree

def get_name(xml):
    name= xml.get('label')
    return name if name!="null" else None

def transform_text(xml):
    name= get_name(xml)
    if name:
        newxml= ElementTree.Element('entity', {"type":"string", "name":name}, text=xml.text)
    else:
        newxml= ElementTree.Element('entity', {"type":"string"}, text=xml.text)
    return newxml

def transform_list(xml):
    name= get_name(xml)
    #t= xml.get('type')
    if name:
        newxml= ElementTree.Element('entity', {"type":"list", "name":name}, text=xml.text)
    else:
        newxml= ElementTree.Element('entity', {"type":"list"}, text=xml.text)
    for child in xml.getchildren():
        assert child.tagname=='el'
        name= get_name(child) or "<link>"
        link= child.get('iref')
        ElementTree.SubElement(newxml, 'entity', {"type":"string", "service":"", "url":link}, text=name)
    return newxml

def transform_record(xml):
    newxml= ElementTree.Element('entity', {"type":"record"})
    for child in xml.getchildren():
        newxml.append( transform_element(child) )
    return newxml
    

def transform_element(xml):
    if xml.tagname=='record':
        return transform_record(xml)
    if xml.tagname=='list':
        return transform_list(xml)
    if xml.tagname=='text':
        return transform_text(xml)
    
    

def transform_xml(xml):
    assert xml.tagname==xml
    l= xml.getchildren()
    assert len(l)==1
    data= l[0]
    assert data.tagname=='data'
    l= data.getchildren()
    assert len(l)==1
    element= l[0]
    return transform_element(xml)
        
