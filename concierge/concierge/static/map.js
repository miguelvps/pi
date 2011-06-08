
// When map page opens get location and display map
$('div').live("pagecreate", function() {     

    //boston :)
    var lat = 38.66097,
        lng = -9.203217;

    var latlng = new google.maps.LatLng(lat, lng);
    var myOptions = {
        zoom: 17,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById("map-canvas"),myOptions);
    
    var bermudaTriangle;


    var triangleCoords = [
        new google.maps.LatLng(25.774252, -80.190262),
        new google.maps.LatLng(18.466465, -66.118292),
        new google.maps.LatLng(32.321384, -64.75737),
        new google.maps.LatLng(25.774252, -80.190262)
    ];

    // Construct the polygon
    // Note that we don't specify an array or arrays, but instead just
    // a simple array of LatLngs in the paths property
    bermudaTriangle = new google.maps.Polygon({
        paths: triangleCoords,
        strokeColor: "#FF0000",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#FF0000",
        fillOpacity: 0.35
    });

    bermudaTriangle.setMap(map);
});   
