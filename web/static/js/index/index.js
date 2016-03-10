/**
 * Created by peyton on 2/18/16.
 */


var markers = []
var tracked_runner = null;

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
                        currentMarker = new MarkerWithLabel({
                            position: countLatLng,
                            map: map,
                            labelContent: box.count.toString(),
                            labelAnchor: new google.maps.Point(15, 7),
                            labelClass: "labels", // the CSS class for the label
                            icon: pinSymbol('#383838'),
                            title: 'clusterCount'
                        })
                        $(currentMarker).data("lat", box.latitude)
                        $(currentMarker).data("lng", box.longitude)
                        google.maps.event.addListener(currentMarker, "click", function (e) {
                            if(runners_table == undefined)
                            {
                                $.fn.DataTable.ext.pager.numbers_length = 3;
                                runners_table = $("#runner_cluster_table").DataTable({
                                    ajax: {
                                        url: '/get_cluster_runners',
                                        data:{lat: $(this).data("lat"),
                                        lng: $(this).data("lng"),
                                        radius: (Math.pow(2, 10 - map.zoom) * 4),}
                                    },

                                    //'bPaginate': false,
                                    'bLengthChange': false,
                                    'bInfo': false,
                                    'bProcessing': false,
                                    'bAutoWidth': false,
                                    'bServerSide': false,
                                    'bFilter': false,
                                    //'bJQueryUI': true,
                                    'sPaginationType': "simple_numbers",
                                    'iDisplayLength': 5,
                                });
                                $("#runner_table_overlay").show()

                            }
                            else
                            {
                              runners_table.ajax.reload();

                            }
                        });
                        markers.push({marker:currentMarker, center:box.latitude + " " +box.longitude});

                    }
                });
                if (tracked_runner != null) {
                    $.ajax({
                        url: 'get_runner_lat_lon',
                        data: {
                            'id': $("#runner_id").data("id")
                        },
                        success: function (data) {
                            var latlng = data.split(',')
                            var newPosition = {lat:parseFloat(latlng[0].substr(1)), lng: parseFloat(latlng[1])};
                            tracked_runner.setMap(null)
                            tracked_runner = new MarkerWithLabel({
                                position: newPosition,
                                map: map,
                                labelContent: '',
                                labelInBackground: false,
                                icon: trackedRunner('#1CD434'),
                                title: 'Tracked Runner',
                            });
                            //tracked_runner.setPosition(newPosition)
                            tracked_runner.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
                        }
                    });
                }
            }
        })
    })
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

            for(var i = 0; i < jsonData.clusters.length; i++)
            {
                var box = jsonData.clusters[i]
                var exists = false;
                var cluserId = 0;
                $.each(markers, function (j, v) {
                    if(markers[j].center == (box.latitude + " " + box.longitude))
                    {
                        exists = true;
                        clusterId = j
                    }
                });

                if(box.count > 0)
                {
                    if(exists)
                    {
                        markers[clusterId].marker.labelContent = box.count.toString();
                        markers[clusterId].marker.label.draw()
                    }
                    else
                    {
                        var countLatLng = {lat: box.latitude, lng: box.longitude};
                        currentMarker = new MarkerWithLabel({
                            position: countLatLng,
                            map: map,
                            labelContent: box.count.toString(),
                            labelAnchor: new google.maps.Point(15, 7),
                            labelClass: "labels", // the CSS class for the label
                            icon: pinSymbol('#383838'),
                            title: 'clusterCount'
                        })
                        $(currentMarker).data("lat", box.latitude)
                        $(currentMarker).data("lng", box.longitude)
                        google.maps.event.addListener(currentMarker, "click", function (e) {
                            if(runners_table == undefined)
                            {
                                $.fn.DataTable.ext.pager.numbers_length = 3;
                                runners_table = $("#runner_cluster_table").DataTable({
                                    ajax: {
                                        url: '/get_cluster_runners',
                                        data:{lat: $(this).data("lat"),
                                        lng: $(this).data("lng"),
                                        radius: (Math.pow(2, 10 - map.zoom) * 4),}
                                    },

                                    //'bPaginate': false,
                                    'bLengthChange': false,
                                    'bInfo': false,
                                    'bProcessing': false,
                                    'bAutoWidth': false,
                                    'bServerSide': false,
                                    'bFilter': false,
                                    //'bJQueryUI': true,
                                    'sPaginationType': "simple_numbers",
                                    'iDisplayLength': 5,
                                });
                                $("#runner_table_overlay").show()
                            }
                            else
                            {
                              runners_table.ajax.reload();

                            }

                        });
                        markers.push({marker:currentMarker, center:box.latitude + " " +box.longitude});

                    }
                }else if (box.count == 0 && exists)
                {
                    markers[clusterId].marker.setMap(null);
                    markers.splice(clusterId, 1);
                    i--;
                }
            }

            jsonData.clusters.forEach(function (box) {
                var exists = false
                var clusterId = 0;
                $.each(markers, function (j, v) {
                    if(markers[j].center == (box.latitude + " " + box.longitude))
                    {
                        exists = true;
                        clusterId = j
                    }
                });
                if (box.count > 0) {

                    if(exists) {

                        markers[clusterId].marker.labelContent = box.count.toString();
                        markers[clusterId].marker.label.draw()
                        i++;
                    }
                    else
                    {

                        i++;
                    }
                }else if(box.count > 0 && exists)
                {
                    markers[clusterId].marker.setMap(null);
                    markers.splice(clusterId, 1);
                }
            });
            if (tracked_runner != null) {
                $.ajax({
                    url: 'get_runner_lat_lon',
                    data: {
                        'id': $("#runner_id").data("id")
                    },
                    success: function (data) {
                        var latlng = data.split(',')
                        var newPosition = {lat:parseFloat(latlng[0].substr(1)), lng: parseFloat(latlng[1])};
                        tracked_runner.setPosition(newPosition)
                    }
                });
            }
        }
    });
}

function clearMarkers() {
    for (var i = 0; i < markers.length; i++) {
        markers[i].marker.setMap(null)
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
        scale: 20,
    };
}
function trackedRunner(color) {
    return {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: color,
        fillOpacity: 1,
        strokeColor: '#000',
        strokeWeight: 2,
        scale: 10,
    };
}
$(document).ready(function () {

    $("#runnerSearch").select2({
        ajax: {
            url: "http://" + location.hostname + ":8983/solr/runr.runners/suggest",
            dataType: "jsonp",
            jsonpCallback: 'callback',
            delay: 250,
            data: function (params) {
                return {
                    'spellcheck.q': params.term, // search term
                    wt: 'json',
                    'json.wrf': "callback",
                    'shards.qt':'/suggest',
                };
            },
            processResults: function (data, params) {
                $('#runnerSearch').empty();
                if (data.spellcheck.suggestions.length > 0) {
                    suggestions = []
                    $.each(data.spellcheck.suggestions[1].suggestion, function (i, v) {
                        var suggestionArray = v.word.split('_')
                        suggestions.push({
                            "id": i,
                            "suggestion": suggestionArray[0],
                            "runner_id": suggestionArray[1]
                        })
                    });
                    return {
                        results: suggestions,
                    };
                }
                else {
                    return {
                        results: []
                    }
                }
            },

            cache: true,

        },
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        minimumInputLength: 1,
        placeholder: 'Search For Runner By Name',
        templateResult: suggestionFormat, // omitted for brevity, see the source of this page
        templateSelection: suggestionSelectionRepo // omitted for brevity, see the source of this page
    });

    function suggestionFormat(suggestions) {
        if (suggestions.loading) return "Loading"
        if (suggestions != undefined) {
            var markup = "<div class='select2-result-suggestion'><b>" + suggestions.suggestion + "</b></div>";
            return markup;
        }
        return ""
    }

    function suggestionSelectionRepo(suggestions) {
        return suggestions.suggestion || 'Search For Runner By Name'
    }

    $("#runnerSearch").on("select2:select", function (e) {
        var selection = $($(this)).select2('data')
        if (selection.length == 1) {
            searchForRunner(selection[0].runner_id)
        }
    });

    function searchForRunner(runnerName) {
        $.ajax({
            'url': '/search_for_runner',
            'data': {
                'query': runnerName
            },
            success: function (data) {
                runner_object = JSON.parse(data);
                if (runner_object.weight != '') {
                    $("#runner_weight").text("Weight:" + runner_object.weight);
                    $("#runner_name").text(runner_object.given_name);
                    $("#runner_average_speed").text("Average Speed:" + runner_object.average_speed + " Km/hr");
                    $("#runner_age").text("Age:" + runner_object.age)
                    $("#runner_id").data("id", runner_object.id)
                    $("#runner_projected_finish").text("Projected Finish:" + runner_object.projected_finish)

                    var latlng = runner_object.lat_lng.split(',')
                    var runnerTrack = {lat: parseFloat(latlng[0]), lng: parseFloat(latlng[1])};
                    if(tracked_runner == null) {
                        tracked_runner = new MarkerWithLabel({
                            position: runnerTrack,
                            map: map,
                            labelContent: '',
                            labelInBackground: false,
                            icon: trackedRunner('#1CD434'),
                            title: 'Tracked Runner',
                        });
                        tracked_runner.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);

                    }
                    else {
                        tracked_runner.setPosition(runnerTrack);
                    }
                }
            }
        })
    }
});
function updateTimer() {
    $.ajax({
        'url': '/get_timer_tick',
        success: function (time) {
            $("#timerText").text(pad(Math.floor(time / 3600), 2) + ":" + pad(Math.floor((time % 3600) / 60), 2) + ":" + pad(time % 60, 2))

        }
    })
}

function pad(n, width) {
    var n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join('0') + n;
}

$.ajax({
    url: '/get_scatter_plot_data',
    success: function (data) {
        var parsedData = JSON.parse(data)
        var trace = {
            x: parsedData.x,
            y: parsedData.y,
            z: parsedData.z,
            mode: 'markers',
            marker: {
                size: 3,
                line: {
                    color: 'rgba(217, 217, 217, 0.14)',
                    width: 0.25
                },
            },

            type: 'scatter3d'
        };
        var data = [trace];
        var layout = {
            scene: {
                xaxis: {
                    title: 'Weight',
                    titlefont: {
                        size: 10,
                        color: '#ffffff'
                    },
                    tickfont: {
                        size: 10,
                        color: '#ffffff'
                    },
                },
                yaxis: {
                    title: 'Height',
                    titlefont: {
                        size: 10,
                        color: '#ffffff'
                    },
                    tickfont: {
                        size: 10,
                        color: '#ffffff'
                    },
                },
                zaxis: {
                    title: 'Age',
                    titlefont: {
                        size: 10,
                        color: '#ffffff'
                    },
                    tickfont: {
                        size: 10,
                        color: '#ffffff'
                    },
                },
            },

            margin: {
                l: 0,
                r: 0,
                b: 0,
                t: 0
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
        };
        Plotly.newPlot('piechart', data, layout, {displayModeBar: false});
    }
})


$("#expandChart").click(function () {
    $("#expandedChartView").toggle();
    $.ajax({
        url: '/get_scatter_plot_data',
        success: function (data) {
            var parsedData = JSON.parse(data)
            var trace = {
                x: parsedData.x,
                y: parsedData.y,
                z: parsedData.z,
                mode: 'markers',
                marker: {
                    size: 3,
                    line: {
                        color: 'rgba(217, 217, 217, 0.14)',
                        width: 0.25
                    },
                },

                type: 'scatter3d'
            };
            var data = [trace];
            var layout = {
                scene: {
                    xaxis: {
                        title: 'Weight',
                        titlefont: {
                            size: 10,
                            color: '#ffffff'
                        },
                        tickfont: {
                            size: 10,
                            color: '#ffffff'
                        },
                    },
                    yaxis: {
                        title: 'Height',
                        titlefont: {
                            size: 10,
                            color: '#ffffff'
                        },
                        tickfont: {
                            size: 10,
                            color: '#ffffff'
                        },
                    },
                    zaxis: {
                        title: 'Age',
                        titlefont: {
                            size: 10,
                            color: '#ffffff'
                        },
                        tickfont: {
                            size: 10,
                            color: '#ffffff'
                        },
                    },
                },

                margin: {
                    l: 0,
                    r: 0,
                    b: 0,
                    t: 0
                },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
            };
            Plotly.newPlot('expandedPieChart', data, layout, {displayModeBar: false});
        }
    })
})