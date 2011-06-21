from common.awesomexml import AwesomeXml
from xml.etree import ElementTree

def get_name(xml):
    name= xml.get('label')
    return name if name!="null" else None

def transform_text(xml):
    name= get_name(xml)
    if name:
        newxml= ElementTree.Element('entity', {"type":"string", "name":name})
        newxml.text=text=xml.text
    else:
        newxml= ElementTree.Element('entity', {"type":"string"})
        newxml.text=xml.text
    return newxml

def transform_list(xml):
    name= get_name(xml)
    #t= xml.get('type')
    if name:
        newxml= ElementTree.Element('entity', {"type":"list", "name":name})
        newxml.text=xml.text
    else:
        newxml= ElementTree.Element('entity', {"type":"list"})
        newxml.text=xml.text
    for child in xml.getchildren():
        ElementTree.append(transform_list_element(child))
    return newxml

def transform_list_element(xml):
    assert xml.tag=='el'
    link= xml.get('iref')
    name= get_name(xml) or ("<link>" if link else "")
    newxml= ElementTree.Element('entity', {"type":"string", "service":"", "url":link})
    newxml.text= name
    return newxml
    

def transform_record(xml):
    newxml= ElementTree.Element('entity', {"type":"record"})
    for child in xml.getchildren():
        newxml.append( transform_element(child) )
    return newxml
    

def transform_element(xml):
    if xml.tag=='record':
        return transform_record(xml)
    if xml.tag=='list':
        return transform_list(xml)
    if xml.tag=='text':
        return transform_text(xml)
    if xml.tag=='el':
        return transform_list_element(xml)
    
    

def transform_xml(xml):
    assert xml.tag==xml
    l= xml.getchildren()
    assert len(l)==1
    data= l[0]
    assert data.tag=='data'
    l= data.getchildren()
    assert len(l)==1
    element= l[0]
    return transform_element(xml)
        
