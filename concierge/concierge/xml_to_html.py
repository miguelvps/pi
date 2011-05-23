from common import xml_types

from xml.etree import ElementTree

def xml_to_html_aux(xml):
    '''transforms a elementtree element object into html'''
    if xml.get('type')== xml_types.LIST_TYPE:
        html_children= "".join(map(xml_to_html_aux, xml.getchildren()) )
        return list_type(xml, html_children)
    else:
        return generic_type(xml)
        
def list_type(xml, html_children):
    r, k = xml.get('representative'), xml.get('kind')
    list_str= "%s: %s" % (k,r) if (k and r) else k or "List"
    list_header= '<h3>%s</h3>' % list_str
    data_collapsed= "true" if k else "false"
    return '<div data-role="collapsible" data-collapsed="%s" >%s%s</div>' % (data_collapsed, list_header,html_children)


def generic_type(xml):
    k, t= xml.get('kind'), xml.text
    return '<p>%s: %s</p>' % ( k, t )

    
def xml_to_html(xml_str):
    assert type(xml_str)==str or type(xml_str)==unicode
    xml= ElementTree.fromstring(xml_str.encode('utf-8'))
    return xml_to_html_aux(xml)


