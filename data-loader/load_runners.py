from cassandra.cluster import Cluster
from decimal import *
import csv

cluster = Cluster()
session = cluster.connect("runr")

truncate_runners = session.prepare('''
    truncate runr.runners
''')

session.execute(truncate_runners)
print("Loading Runners")
with open('runner_stats_final.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    i = 0

    for row in reader:
        if row[10] != 'NaN' and row[11] != 'NaN' and row[12] != 'NaN':
            print("Loading row {}".format(row[0]))
            runner = {
                    "runner_id":row[0],
                    "first_name":row[1],
                    "last_name":row[2],
                    "given_name":row[3],
                    "birth_country":row[4],
                    "birth_state":row[5],
                    "birth_city":row[6],
                    "birth_year":int(row[7]),
                    "birth_month":int(row[8]),
                    "birth_day":int(row[9]),
                    "weight":int(row[10]),
                    "height":int(row[11]),
                    "base_speed":Decimal(row[12]),
                }

            insert_runner = session.prepare('''
                INSERT INTO runr.runners
                    (runner_id, first_name, last_name, given_name, birth_country, birth_state, birth_city, birth_year, birth_month, birth_day, weight, height, base_speed)
                VALUES
                    (?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''')
            session.execute(insert_runner.bind(runner))
            position = {
                    "runner_id":row[0],
                    "base_speed":Decimal(row[12]),
                    "lat_lng": "40.61572,-74.03123",
                    "location": 0,
                    "location_exact": 0,
                    "starting_position": i/100,
                }

            initialize_runner_position = session.prepare('''
                INSERT INTO runr.position
                    (runner_id, base_speed, lat_lng, location, location_exact, starting_position)
                VALUES
                    (?,?,?,?,?, ?)
            ''')
            i += 1


            session.execute(initialize_runner_position.bind(position))