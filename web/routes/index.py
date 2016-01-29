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