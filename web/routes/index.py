import logging
import time
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

@index_api.route('/get_route_coordinates')
def get_route_coordinates():
    get_route_coordinates = cassandra_helper.session.prepare('''
        SELECT location_id, latitude_degrees, longitude_degrees
        FROM runr.points_by_distance
    ''')
    coordinates = cassandra_helper.session.execute(get_route_coordinates)

    sorted_coordinates = []
    sorted_coordinates.append({
                    "location_id": coordinates[0]["location_id"],
                    "lat": coordinates[0]["latitude_degrees"],
                    "lng": coordinates[0]["longitude_degrees"]})
    i = 1
    for row in coordinates:
        if i % 10 == 0:
            sorted_coordinates.append({
                "location_id": row["location_id"],
                "lat": row["latitude_degrees"],
                "lng": row["longitude_degrees"]})
        i += 1
        # for j in range(0, len(sorted_coordinates)):
        #     if int(row["location_id"]) > int(sorted_coordinates[j]["location_id"]):
        #         sorted_coordinates.insert(j,{
        #             "location_id": row["location_id"],
        #             "lat": row["latitude_degrees"],
        #             "lng": row["longitude_degrees"]})
        #
        #         break;

    return json.dumps(sorted_coordinates)

@index_api.route('/geospatial_clustering')
def geospatial_clustering():
    screenWidth = float(request.args.get('screenWidth'))
    screenHeight = float(request.args.get('screenHeight'))
    latitudeStart = float(request.args.get('latitudeStart'))
    longitudeStart = float(request.args.get('longitudeStart'))
    latitudeDistance = float(request.args.get('latitudeDistance'))
    longitudeDistance = float(request.args.get('longitudeDistance'))

    latPerPx = latitudeDistance / screenHeight
    longPerPx = longitudeDistance / screenWidth

    # Maximum size for the square
    minSize = min(screenWidth, screenHeight)
    # Create 16 square grid
    squareSize = minSize / 4
    # 1920 - 1080 /2 = Right and Left Offset (Start of Grid)
    offset = ((max(screenWidth, screenHeight) - minSize) / 2)

    clusters = []
    if screenWidth > screenHeight:
        for i in range(0,4):
            for j in range(0,4):
                # Start of Grid + Completed Squares
                latOffset = ((i * squareSize)) * latPerPx
                longOffset = abs((offset + (j * squareSize)) * longPerPx)

                # Current Square + Half the Distance = center of square
                squareLat = latitudeStart + (latOffset + ((squareSize / 2) * latPerPx))
                squareLong = longitudeStart + (longOffset + ((squareSize / 2) * longPerPx))
                if squareLong >= 180:
                    squareLong -= 180
                    squareLong *= -1
                elif squareLong <= -180:
                    squareLong += 180
                    squareLong *= -1

                if squareLat <= -90:
                    squareLat += 90
                    squareLat *= -1
                elif squareLat >= 90:
                    squareLat -= 90
                    squareLat *= -1

                squareDistance = abs((squareSize / 2) * latPerPx)
                solrParams = '{"q": "*:*", "fq": "{!bbox sfield=lat_lng pt=' + str(squareLat) + ',' + str(squareLong) + ' d=' + str(squareDistance * 110.574) + '}"}'
                geoCount = cassandra_helper.session.execute("select count(*) from runr.position where solr_query='" + solrParams + "'")
                clusters.append({"latitude":squareLat, "longitude":squareLong, "count":geoCount.current_rows[0]["count"]})
    return json.dumps(clusters)

@index_api.route('/get_unique_runner_positions')
def get_unique_runner_positions():
    session = cassandra_helper.session
    get_distinct_positions = session.prepare('''
        SELECT *
        FROM runr.position
    ''')


    distinct_positions = session.execute(get_distinct_positions)
    location_ids = set()
    for row in distinct_positions:
        location_ids.add(row["location"])
    ids = ",".join(str(x) for x in sorted(location_ids))
    # print('''
    #     SELECT * FROM points_by_distance
    #     WHERE location_id
    #     IN {}
    # '''.format(",".join(results)))
    get_geocords = session.prepare('''
        SELECT latitude_degrees, longitude_degrees, location_id FROM runr.points_by_distance
        WHERE location_id
        IN ({})
    '''.format(ids))

    lat_lng = session.execute(get_geocords)
    results = []
    for rows in lat_lng:
        results.append({
            "latitude": rows["latitude_degrees"],
            "longitude": rows["longitude_degrees"],
            "location_id": rows["location_id"]
        })

    return json.dumps(results)