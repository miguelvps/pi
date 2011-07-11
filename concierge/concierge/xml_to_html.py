from concierge.services_models import Service
from xml.etree import ElementTree
from flask import render_template

def render_string(xml):
    return xml.text

def render_email(xml):
    return '<a href="mailto:%s">%s</a>' % (xml.text, xml.text)

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
        if geowkt[:9] == 'POLYGON((':
            assert geowkt[-2:] == '))'
            geowkt = geowkt[9:-2] 
            pair_list = geowkt.split(', ')
            tuple_list = map(lambda s: tuple([float(a) for a in s.split(' ')]), pair_list)
            return (tuple_list, 'polygon')
        else:
            raise Exception("geowkt parse error")

    def get_bounds(coords):
        min_coords = reduce(lambda (x,y),(z,w): (min(x,z), min(y,w)) ,coords)
        max_coords = reduce(lambda (x,y),(z,w): (max(x,z), max(y,w)) ,coords)
        return (min_coords, max_coords)

    geowkt = filter(lambda e: e.get('type') == 'geowkt', xml.getchildren())
    assert len(geowkt) == 1
    coords, wkt_type = parse_geowkt(geowkt[0].text)
    min_coords, max_coords = get_bounds(coords)
    result= render_template('map2.html', min_lat= min_coords[0], min_lng= min_coords[1],
           max_lat= max_coords[0], max_lng= max_coords[1],    
            draw_coords = ",".join(['new google.maps.LatLng(%f, %f)'% (x,y) for (x,y) in coords])
            )
    print result
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
    add_service_id(xml)
    t= xml.get('type')
    try:
        render_function= globals()['render_'+t]
    except:
        raise Exception('Could not find function to render type '+t)
    return construct_link(xml) % (render_function(xml))
