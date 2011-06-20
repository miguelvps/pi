from common.awesomexml import AwesomeXml
from xml.etree import ElementTree

def transform_text(xml):
    name= xml.get('label')
    name = name if name!="null" else None
    if name:
        newxml= ElementTree.Element('entity', {"type":"string", "name":name}, text=xml.text)
    else:
        newxml= ElementTree.Element('entity', {"type":"string"}, text=xml.text)
    return newxml

def transform_record(xml):
    newxml= ElementTree.Element('entity', {"type":"record"})
    for child in xml.getchildren():
        newxml.append( transform_element(child) )
    return newxml
    

def transform_element(xml):
    if xml.tagname=='record':
        return transform_record(xml)
    
    

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
        
