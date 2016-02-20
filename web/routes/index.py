import logging
import time
import numpy
from numpy import array, sort
from LatLon import LatLon, Latitude, Longitude
import datetime
from datetime import date
from orderedset import OrderedSet
from collections import OrderedDict
from cassandra.query import ValueSequence
from helpers import cassandra_helper
try: import simplejson as json
except ImportError: import json

from flask import Flask, Blueprint, render_template, request, session, jsonify

# from routes.rest import get_session, \
#     get_solr_session
app = Flask(__name__)
index_api = Blueprint('black_friday_api', __name__)

cassandra_session = None
solr_session = None
prepared_statements = None


@index_api.route('/')
def index():
    return render_template('index.jinja2')

@index_api.route('/')
def search_suggestions():
    return ""

@index_api.route('/get_scatter_plot_data')
def get_scatter_plot_data():
    get_runners = cassandra_helper.session.prepare('''
    SELECT weight, height, birth_year, birth_month, birth_day FROM runr.runners
    ''')
    runners = cassandra_helper.session.execute(get_runners)
    results = {'x':[],
               'y':[],
               'z':[]}
    today = date.today()

    for runner in runners:
        results['x'].append(runner["weight"])
        results['y'].append(runner["height"])
        results['z'].append(today.year - runner["birth_year"] - ((today.month, today.day) < (runner["birth_month"], runner["birth_day"])))
    return json.dumps(results)

@index_api.route('/get_runner_lat_lon')
def get_runner_lat_lon():
    id = request.args.get("id")
    search_runners = cassandra_helper.session.prepare('''
    SELECT * FROM runr.runner_tracking
    WHERE id=?
    ''')
    runner = cassandra_helper.session.execute(search_runners.bind({'id':id}))
    return json.dumps(runner.current_rows[0]["lat_lng"])

@index_api.route('/search_for_runner')
def search_for_runner():
    query = request.args.get("query")
    search_runners = cassandra_helper.session.prepare('''
    SELECT * FROM runr.runners
    WHERE solr_query=?
    ''')
    search_runner_tracking = cassandra_helper.session.prepare('''
    SELECT * FROM runr.runner_tracking
    WHERE solr_query=?
    ''')
    runner = cassandra_helper.session.execute(search_runners.bind({
        'solr_query': 'id: "' + query + '"'
    }))

    if len(runner.current_rows) > 0:
        runner_position = cassandra_helper.session.execute(search_runner_tracking.bind({
            'solr_query': 'id: "' + query + '"'
        }))
        if len(runner_position.current_rows) == 0:
            raise ValueError("Runner row mismatch")
        today = date.today()
        return json.dumps({
            'id':runner.current_rows[0]["id"],
            'given_name':runner.current_rows[0]["given_name"],
            'weight': runner.current_rows[0]["weight"],
            'age': today.year - runner.current_rows[0]["birth_year"] - ((today.month, today.day) < (runner.current_rows[0]["birth_month"], runner.current_rows[0]["birth_day"])),
            'average_speed': runner_position[0]["average_speed"],
            'lat_lng': runner_position[0]['lat_lng']
        })
    else:
        return json.dumps({
            'id':'',
            'given_name':'',
            'age':'',
            'weight':'',
            'average_speed':'',
            'lat_lng':'',
        })

@index_api.route('/get_timer_tick')
def get_timer_tick():
    get_timer_counter = cassandra_helper.session.prepare('''
    SELECT * FROM runr.time_elapsed
    WHERE counter_name='time_elapsed'
    ''')
    return json.dumps(cassandra_helper.session.execute(get_timer_counter)[0]["time_elapsed"])

@index_api.route('/get_route_coordinates')
def get_route_coordinates():
    sorted_coordinates = get_route_coordinates_helper()
    return json.dumps(sorted_coordinates)

def get_route_coordinates_helper():
    get_route_coordinates = cassandra_helper.session.prepare('''
        SELECT location_id, latitude_degrees, longitude_degrees
        FROM runr.points_by_distance_filtered
    ''')
    coordinates = cassandra_helper.session.execute(get_route_coordinates)
    numpy_coordinates = []
    for row in coordinates:
        numpy_coordinates.append((int(row["location_id"]),
                                float(row["latitude_degrees"]),
                                float(row["longitude_degrees"])))

    dType = [('location_id', int), ('latitude_degrees', float), ('longitude_degrees', float)]

    sorted_coordinates = []

    final_coordinates = numpy.array(numpy_coordinates, dtype=dType)
    for coordinate in numpy.sort(final_coordinates, order='location_id').tolist():
        sorted_coordinates.append({
            "location_id": coordinate[0],
            "lat": coordinate[1],
            "lng": coordinate[2]
        })

    return sorted_coordinates

# @index_api.route('/geospatial_clustering')
# def geospatial_clustering():
#     screenWidth = float(request.args.get('screenWidth'))
#     screenHeight = float(request.args.get('screenHeight'))
#     latitudeStart = float(request.args.get('latitudeStart'))
#     longitudeStart = float(request.args.get('longitudeStart'))
#     latitudeDistance = float(request.args.get('latitudeDistance'))
#     longitudeDistance = float(request.args.get('longitudeDistance'))
#
#     latPerPx = latitudeDistance / screenHeight
#     longPerPx = longitudeDistance / screenWidth
#
#     # Maximum size for the square
#     minSize = min(screenWidth, screenHeight)
#     # Create 16 square grid
#     squareSize = minSize / 4
#     # 1920 - 1080 /2 = Right and Left Offset (Start of Grid)
#     offset = ((max(screenWidth, screenHeight) - minSize) / 2)
#
#     clusters = []
#     if screenWidth > screenHeight:
#         for i in range(0,4):
#             for j in range(0,4):
#                 # Start of Grid + Completed Squares
#                 latOffset = ((i * squareSize)) * latPerPx
#                 longOffset = abs((offset + (j * squareSize)) * longPerPx)
#
#                 # Current Square + Half the Distance = center of square
#                 squareLat = latitudeStart + (latOffset + ((squareSize / 2) * latPerPx))
#                 squareLong = longitudeStart + (longOffset + ((squareSize / 2) * longPerPx))
#                 if squareLong >= 180:
#                     squareLong -= 180
#                     squareLong *= -1
#                 elif squareLong <= -180:
#                     squareLong += 180
#                     squareLong *= -1
#
#                 if squareLat <= -90:
#                     squareLat += 90
#                     squareLat *= -1
#                 elif squareLat >= 90:
#                     squareLat -= 90
#                     squareLat *= -1
#
#                 squareDistance = abs((squareSize / 2) * latPerPx)
#                 solrParams = '{"q": "*:*", "fq": "{!bbox sfield=lat_lng pt=' + str(squareLat) + ',' + str(squareLong) + ' d=' + str(squareDistance * 110.574) + '}"}'
#                 geoCount = cassandra_helper.session.execute("select count(*) from runr.runner_tracking where solr_query='" + solrParams + "'")
#                 clusters.append({"latitude":squareLat, "longitude":squareLong, "count":geoCount[0]["count"]})
#     return json.dumps(clusters)

@index_api.route("/geospatial_search")
def geospatial_search():
    latitudeStart = float(request.args.get('latitudeStart'))
    longitudeStart = float(request.args.get('longitudeStart'))
    latitudeEnd = float(request.args.get('latitudeEnd'))
    longitudeEnd = float(request.args.get('longitudeEnd'))
    radius = float(request.args.get('radius'))
    i = 0
    clusters = []
    results = []
    coordinates = get_route_coordinates_helper()
    start = None
    end = None
    while i < len(coordinates):
        currentCoordinate = coordinates[i]
        if start is None and insideMap(latitudeStart, latitudeEnd, longitudeStart, longitudeEnd, currentCoordinate["lat"], currentCoordinate["lng"]):
            start = currentCoordinate
            solrParams = '{"q": "*:*", "fq": "{!bbox sfield=lat_lng pt=' + str(currentCoordinate["lat"]) + ',' + str(currentCoordinate["lng"]) + ' d=' + str(radius) + '}"}'
            geoCount = cassandra_helper.session.execute("select count(*) from runr.runner_tracking where solr_query='" + solrParams + "'")
            results.append({"latitude":currentCoordinate["lat"], "longitude":currentCoordinate["lng"], "count":geoCount[0]["count"]})
            clusters.append(currentCoordinate)
        # if start != None and not insideMap(latitudeStart, latitudeEnd, longitudeStart, longitudeEnd, currentCoordinate["lat"], currentCoordinate["lng"]):
        #     break;
        if len(clusters) > 0 and insideMap(latitudeStart, latitudeEnd, longitudeStart, longitudeEnd, currentCoordinate["lat"], currentCoordinate["lng"]):

            currentLatLon = LatLon(Latitude(currentCoordinate["lat"]), Longitude(currentCoordinate["lng"]))
            lastClusterLatLon = LatLon(Latitude(clusters[-1]["lat"]), Longitude(clusters[-1]["lng"]))
            distance = abs(currentLatLon.distance(lastClusterLatLon))
            if distance > radius * 2:
                solrParams = '{"q": "*:*", "fq": "{!bbox sfield=lat_lng pt=' + str(currentCoordinate["lat"]) + ',' + str(currentCoordinate["lng"]) + ' d=' + str(radius) + '}"}'
                geoCount = cassandra_helper.session.execute("select count(*) from runr.runner_tracking where solr_query='" + solrParams + "'")
                # if geoCount[0]["count"] > 0:
                results.append({"latitude":currentCoordinate["lat"], "longitude":currentCoordinate["lng"], "count":geoCount[0]["count"]})
                clusters.append(currentCoordinate)
        i += 10


    return json.dumps({"clusters": results})

def insideMap(latStart, latEnd, lngStart, lngEnd, lat, lng):
    if lat < latStart and lat > latEnd and lng > lngStart and lng < lngEnd:
        return True
    return False
