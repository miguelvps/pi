from common import xml_types

from xml.etree import ElementTree
from flask import render_template
import itertools


class AtributeTypeRepresentation(object):
    '''represents a xml_type. consists of a tuple with a name and a url'''
    def __init__(self, name, url):
        assert type(name)==str or type(name)==unicode
        assert type(url)==str or type(url)==unicode
        self.name= name
        self.url= url

class ListTypeRepresentation(object):
    '''represents a xml_type on concierge. consists of a tuple whose
    first element is the page title and the second is a list of tuples
    of (text,url)'''
    def __init__(self, name, atribute_list):
        assert type(name)==str or type(name)==unicode
        assert all(map(lambda a: type(a)== AtributeTypeRepresentation, atribute_list))
        self.name= name
        self.content= atribute_list
    
    @staticmethod
    def from_list(l, name="List"):
        '''takes a list of ListTypeRepresentation, creates a new one with
        all of their content'''
        assert all([isinstance(a, ListTypeRepresentation) for a in l])
        #concatenate all lists into one
        content= reduce(lambda x,y: x.extend(y), [other.content for other in l]) if len(l) else []
        return ListTypeRepresentation(name, content)


#-----------------------------------------------------------------------


def list_type_shallow_representation(xml):
    r, k = xml.get('xml_name'), xml.get('xml_kind')
    title= "%s: %s" % (k,r) if (k and r) else k or "List"
    return AtributeTypeRepresentation(title, '')

def list_or_atribute_type_shallow_representation(xml):
    if xml.get('xml_type')== xml_types.LIST_TYPE:
        return list_type_shallow_representation(xml)
    else:
        k, t= xml.get('kind'), xml.text
        title= '<p>%s: %s</p>' % ( k, t )
        return AtributeTypeRepresentation(title, '')

def list_type_deep_representation(xml):
    r, k = xml.get('representative'), xml.get('kind')
    title= "%s: %s" % (k,r) if (k and r) else k or "List"
    atributes= map(list_or_atribute_type_shallow_representation, xml.getchildren())
    return ListTypeRepresentation(title, atributes)


#-----------------------------------------------------------------------

    
def xml_to_representation(xml_str):
    assert type(xml_str)==str or type(xml_str)==unicode
    xml= ElementTree.fromstring(xml_str.encode('utf-8'))
    if xml.get('type')== xml_types.LIST_TYPE:
        return list_type_deep_representation(xml)
    else:
        return list_or_atribute_type_shallow_representation(xml)


def render_xml_list(xml_list):
    rs= map(xml_to_representation, xml_list)
    r= ListTypeRepresentation.from_list(rs)
    return render_template('results_model_list.html', l=r)
