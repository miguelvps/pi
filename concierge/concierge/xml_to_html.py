from concierge.services_models import Service
from xml.etree import ElementTree

def render_string(xml):
    return xml.text

def render_email(xml):
    return '<a href="mailto:%s">%s</a>' % (xml.text, xml.text)

def render_image(xml):
    return '<img src="%s"/>' % (element.text)

def render_list(xml):
    html= '<ul data-role="listview" data-inset="true">'
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
    return
    '''
    {% elif element.get('type') == "map" %}
-    <link rel="stylesheet" href="/static/map.css" />
-    <script type="text/javascript">
-        // When map page opens get location and display map
-        $('div').live("pagecreate", function() {         
-     
-
-            var lat = 38.66097,
-                lng = -9.203217;
-
-            var latlng = new google.maps.LatLng(lat, lng);
-            var myOptions = {
-                zoom: 17,
-                center: latlng,
-                mapTypeId: google.maps.MapTypeId.ROADMAP
-            };
-            var map = new google.maps.Map(document.getElementById("map-canvas"),myOptions);
-            
-            var str = String("{{element[2].text}}"); 
-
-            var polygon;
-
-            var triangleCoords = [
-                new google.maps.LatLng(25.774252, -80.190262),
-                new google.maps.LatLng(18.466465, -66.118292),
-                new google.maps.LatLng(32.321384, -64.75737),
-                new google.maps.LatLng(25.774252, -80.190262)
-            ];
-
-            // Construct the polygon
-            // Note that we don't specify an array or arrays, but instead just
-            // a simple array of LatLngs in the paths property
-            polygon = new google.maps.Polygon({
-                paths: triangleCoords,
-                strokeColor: "#FF0000",
-                strokeOpacity: 0.8,
-                strokeWeight: 2,
-                fillColor: "#FF0000",
-                fillOpacity: 0.35
-            });
-
-            polygon.setMap(map);
-        }); 
-        </script>
-        <div id="map-canvas">
-            <!-- map loads here... -->
-        </div>
    '''

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
    
