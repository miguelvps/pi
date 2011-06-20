from concierge.services_models import Service
from xml.etree import ElementTree
from concierge import xml_to_html_g7

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
    html ='''
    <style>
        .page-map, .ui-content, #map-canvas { width: 100%%; height: 100%%; padding: 0; }
    </style>
    <script type="text/javascript"> 
        // When map page opens get location and display map

            var min_latlng = new google.maps.LatLng(%(min_lat)s, %(min_lng)s);
            var max_latlng = new google.maps.LatLng(%(max_lat)s, %(max_lng)s);

            var bounds = new google.maps.LatLngBounds(min_latlng, max_latlng);

            var myOptions = {
                zoom: 12,
                center: bounds.getCenter(),
                mapTypeId: google.maps.MapTypeId.SATELLITE
            };

            var map = new google.maps.Map(document.getElementById("map-canvas"),myOptions);
            google.maps.event.trigger(map,'resize');

            map.fitBounds(bounds);

            var polygon;

            var myCoords = [%(draw_coords)s];

            // Construct the polygon
            // Note that we don't specify an array or arrays, but instead just
            // a simple array of LatLngs in the paths property
            polygon = new google.maps.Polygon({
                paths: myCoords,
                strokeColor: "#FF0000",
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: "#FF0000",
                fillOpacity: 0.35
           });
           polygon.setMap(map);
           var markerOptions = {
                position: bounds.getCenter(),
                map: map,
                title: "title",
           };
           var marker = new google.maps.Marker(markerOptions);

       $('.page-map').live('pageshow',function(){
            google.maps.event.trigger(map, 'resize');
            map.setOptions(myOptions); 
            map.fitBounds(bounds);
        });

        </script>
        <div id="map-canvas">
        </div>
    ''' % {'min_lat': min_coords[0], 'min_lng': min_coords[1],
           'max_lat': max_coords[0], 'max_lng': max_coords[1],    
            'draw_coords' : ",".join(['new google.maps.LatLng(%f, %f)'% (x,y) for (x,y) in coords]),
            }

    return html

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
    if xml.tag=='data':
        #Group 07 xml
        xml= xml_to_html_g7.transform_xml(xml)

    assert xml.tag=='entity'
    add_service_id(xml)
    t= xml.get('type')
    try:
        render_function= globals()['render_'+t]
    except:
        raise Exception('Could not find function to render type '+t)
    return construct_link(xml) % (render_function(xml))
    
    return
