from cassandra.cluster import Cluster
from decimal import *
from datetime import date
import time
from datetime import datetime, timedelta
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
    today = date.today()
    for row in reader:
        if row[10] != 'NaN' and row[11] != 'NaN' and row[12] != 'NaN':
            runner = {
                    "id":row[0],
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
                    'age': today.year - int(row[7]) - ((today.month, today.day) < (int(row[8]), int(row[9]))),
                    "given_name_id": row[3] + "_" + row[0],
                }

            insert_runner = session.prepare('''
                INSERT INTO runr.runners
                    (id, first_name, last_name, given_name, birth_country, birth_state, birth_city, birth_year, birth_month, birth_day, weight, height,given_name_id,age)
                VALUES
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''')
            session.execute(insert_runner.bind(runner))
            position = {
                    "id":row[0],
                    "given_name":row[3],
                    "date":datetime.utcnow(),
                    "speed":Decimal(row[12]),
                    "lat_lng": "40.61572,-74.03123",
                    "distance": 0,
                    "distance_actual": 0,
                    "starting_position": (i/100) + ((i/100) * 10),
                    "average_speed": Decimal(row[12])
                }

            initialize_runner_position = session.prepare('''
                INSERT INTO runr.runner_tracking
                    (id, given_name, date, speed, lat_lng, distance, distance_actual, starting_position, average_speed)
                VALUES
                    (?,?,?,?,?,?,?,?,?)
            ''')
            i += 1


            session.execute(initialize_runner_position.bind(position))

