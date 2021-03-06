from concierge.services_models import Service
from xml.etree import ElementTree
from concierge import xml_to_html_g7
from flask import render_template

def render_string(xml):
    return xml.text

def render_email(xml):
    return '<a href="mailto:%s">%s</a>' % (xml.text, xml.text)

def render_url(xml):
    return '<a href="%s">%s</a>' % (xml.text, xml.text)
    
def render_image(xml):
    return '<img src="%s"/>' % (xml.text)

def render_list(xml):
    html= '<ul data-role="listview" data-inset="true" class="list">'
    for child in xml:
        child_html= render(child)
        html += '<li>%s</li>' % (child_html)
    html+='</ul>'
    return html

def render_record(xml):
    html= '<h1>%s</h1> <dl>' % (xml[0].text)
    for child in xml[1:]:
        html+= '<dt><h4>%s</h4></dt>' % child.get('name', '')
        html+= '<dd>%s</dd>' % (render(child))
    html+='</dl>'
    return html

def render_map(xml):

    def parse_geowkt(geowkt):
        assert geowkt[-2:] == '))'
        if geowkt[:9] == 'POLYGON((':
            t= "Polygon"
            geowkt = geowkt[9:-2] 
        elif geowkt[:10] == 'POLYLINE((':
            t= "Polyline"
            geowkt = geowkt[10:-2]         
        else:
            raise Exception("geowkt parse error")
        
        pair_list = geowkt.split(', ')
        tuple_list = map(lambda s: tuple([float(a) for a in s.split(' ')]), pair_list)
        return (tuple_list, t)

    def get_bounds(coords):
        min_coords = reduce(lambda (x,y),(z,w): (min(x,z), min(y,w)) ,coords)
        max_coords = reduce(lambda (x,y),(z,w): (max(x,z), max(y,w)) ,coords)
        return (min_coords, max_coords)
        
    children= xml.getchildren()
    geowkts = filter(lambda e: e.get('type') == 'geowkt', children)
    geowkts = map(lambda e: e.text , geowkts)
    
    if len(geowkts) == 1:
        #polygon
        coords, wkt_type = parse_geowkt(geowkts[0])
        assert wkt_type== 'Polygon'
        min_coords, max_coords = get_bounds(coords)
        
        info_html = '<h2> %s </h2><dl>' % xml[0].text
        for child in xml.getchildren()[1:]:
            if child.get('type') == 'geowkt':
                geowkt = child.text
            else:
                info_html+= '<dt><h4>%s</h4></dt>' % child.get('name', '')
                info_html+= '<dd>%s</dd>' % (render(child))
        info_html += '</dl>'
        
        descriptions= [info_html]
        coords= [coords]
        coord_desc_pairs= [(coords, info_html)]
        
    if len(geowkts)>1:
        #route
        descriptions= filter(lambda e: e.get('type') == 'string', children)
        descriptions= map(lambda e: e.text, descriptions)
        descriptions=descriptions[1:]   # first string is title, each other is the description of geowkt
        assert len(descriptions)==len(geowkts)
        coords, type_list= zip(*map(parse_geowkt, geowkts))
        assert all([t=="Polyline" for t in type_list])
        wkt_type="Polyline"
        
        all_coords= []
        for l in coords:
            all_coords.extend(l)
        min_coords, max_coords = get_bounds(all_coords)

    javascript_coords= map(lambda cs: ",".join(['new google.maps.LatLng(%f, %f)'% (x,y) for (x,y) in cs]), coords);
    coord_desc_pairs= zip(javascript_coords, descriptions)
    
    result= render_template('map2.html',
    min_lat= min_coords[0], min_lng= min_coords[1], max_lat= max_coords[0], max_lng= max_coords[1],    
    wkt_type= wkt_type, coord_desc_pairs=coord_desc_pairs)
        
    return result


def add_service_id(xml):
    service= xml.get('service')
    if service:
        s = Service.query.filter_by(name=xml.attrib['service']).first()
        if s:
            xml.attrib['service_id']= s.id

def construct_link(xml):
    service_id, url, kind= map(xml.get, ('service_id','url','kind'))
    if service_id and url:
        return ('<a href="/services/%s/browse%s">' % (service_id,url))+"%s"+'</a>'
    elif kind:
        return ('<a href="/search?query=%s %s">' % (kind, xml.text))+"%s"+'</a>'
    else:
        return "%s"

def render(xml):
    assert isinstance(xml, ElementTree._ElementInterface)
    if xml.tag!='entity':
        #Group 07 xml
        xml= xml_to_html_g7.transform_element(xml)

    assert xml.tag=='entity'
    add_service_id(xml)
    t= xml.get('type')
    try:
        render_function= globals()['render_'+t]
    except:
        raise Exception('Could not find function to render type '+t)
    return construct_link(xml) % (render_function(xml))
    
    return
