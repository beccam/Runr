/**
 * Created by peyton on 2/18/16.
 */
var markers = []
function initMap() {
    map = new google.maps.Map(document.getElementById('google-map'), {
        zoom: 10,
        minZoom: 10,
        maxZoom: 18,
        center: {lat: 40.621906, lng: -74.032435},
        streetViewControl: false,
        mapTypeControl: false,
    });

    $.ajax({
        url: '/get_route_coordinates',
        success: function (data) {

            polyLineCoordinates = JSON.parse(data);
            var path = new google.maps.Polyline({
                path: polyLineCoordinates,
                geodesic: true,
                strokeColor: '#009db2',
                strokeOpacity: 1.0,
                strokeWeight: 4
            });

            path.setMap(map);
        }
    })
    google.maps.event.addListener(map, 'idle', function () {
        $.ajax({
            url: '/geospatial_search',
            data: {
                latitudeStart: map.getBounds().getNorthEast().lat(),
                longitudeStart: map.getBounds().getSouthWest().lng(),
                latitudeEnd: map.getBounds().getSouthWest().lat(),
                longitudeEnd: map.getBounds().getNorthEast().lng(),
                radius: (Math.pow(2, 10 - map.zoom) * 4),
            },
            success: function (data) {
                jsonData = JSON.parse(data)
                clearMarkers();
                jsonData.clusters.forEach(function (box) {
                    if (box.count > 0) {
                        var countLatLng = {lat: box.latitude, lng: box.longitude};
                        markers.push(new MarkerWithLabel({
                            position: countLatLng,
                            map: map,
                            labelContent: box.count.toString(),
                            labelAnchor: new google.maps.Point(15, 7),
                            labelClass: "labels", // the CSS class for the label
                            labelInBackground: false,
                            icon: pinSymbol('#383838'),
                            title: 'clusterCount'
                        }));
                        google.maps.event.addListener(markers[markers.length - 1], "click", function (e) {
                            console.log($(this))
                            $("#clusterCount").text("Total Cluster Count: " + $(this)[0].labelContent)
                        });
                    }
                });
            }
        })
    });
}
function updateClusterMarkers() {
    $.ajax({
        url: '/geospatial_search',
        data: {
            latitudeStart: map.getBounds().getNorthEast().lat(),
            longitudeStart: map.getBounds().getSouthWest().lng(),
            latitudeEnd: map.getBounds().getSouthWest().lat(),
            longitudeEnd: map.getBounds().getNorthEast().lng(),
            radius: (Math.pow(2, 10 - map.zoom) * 4),
        },
        success: function (data) {
            jsonData = JSON.parse(data)
            var i = 0;
            jsonData.clusters.forEach(function (box) {

                if (box.count > 0) {
                    markers[i].labelContent = box.count.toString();
                    markers[i].label.draw()
                    i++;
                }
            });
        }
    });
}
function clearMarkers() {
    for (var i = 0; i < markers.length; i++) {
        markers[i].setMap(null)
    }
    markers = []

}
function pinSymbol(color) {
    return {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: color,
        fillOpacity: 1,
        strokeColor: '#000',
        strokeWeight: 2,
        scale: 20
    };
}