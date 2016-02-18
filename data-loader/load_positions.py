from cassandra.cluster import Cluster
from decimal import *

import csv, math

cluster = Cluster()
session = cluster.connect("runr")

truncate_runners = session.prepare('''
    truncate runr.runners
''')

session.execute(truncate_runners)
print("Loading Positions")
with open('trackpoints_updated.csv', 'rU') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    i = 1
    for row in reader:
        # if row[10] != 'NaN' and row[11] != 'NaN' and row[12] != 'NaN':

        point_by_distance = {
                "location_id":long(math.floor(float(row[4]))),
                "altitude_meters":Decimal(row[3]),
                "distance_meters":Decimal(row[4]),
                "latitude_degrees":Decimal(row[1]),
                "longitude_degrees":Decimal(row[2]),
            }

        insert_distance_point = session.prepare('''
            INSERT INTO runr.points_by_distance
                (location_id, altitude_meters, distance_meters, latitude_degrees, longitude_degrees)
            VALUES
                (?,?,?,?,?)
        ''')
        session.execute(insert_distance_point.bind(point_by_distance))

        if i % 10 == 0:
            insert_distance_point_filtered = session.prepare('''
                INSERT INTO runr.points_by_distance_filtered
                    (location_id, altitude_meters, distance_meters, latitude_degrees, longitude_degrees)
                VALUES
                    (?,?,?,?,?)
            ''')
            session.execute(insert_distance_point_filtered.bind(point_by_distance))
        i += 1
