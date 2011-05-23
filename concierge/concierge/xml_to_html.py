from common import xml_types

from xml.etree import ElementTree


def xml_to_html(xml):
    if type(xml)==str or type(xml)==unicode:
        #this is xml in string format
        xml= ElementTree.fromstring(xml.encode('utf-8'))

    if xml.get('type')== xml_types.LIST_TYPE:
        html_children= "".join(map(xml_to_html, xml.getchildren()) )
        r, k = xml.get('representative'), xml.get('kind')
        list_str= "%s: %s" % (k,r) if (k and r) else k or "List"
        list_header= '<h3>%s</h3>' % list_str
        data_collapsed= "true" if k else "false"
        return '<div data-role="collapsible" data-collapsed="%s" >%s%s</div>' % (data_collapsed, list_header,html_children)
    else:
        return '<p>%s</p>' % (xml.get('kind') + ": "+ xml.text )
