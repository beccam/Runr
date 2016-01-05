from pyspark import SparkContext, SparkConf
from cassandra.cluster import Cluster

if __name__ == "__main__":
    cluster = Cluster()
    session = cluster.connect("runr")
    sc = SparkContext(appName="calculate-position")

    get_runners = session.prepare('''SELECT * FROM runr.runners''')
    get_position = session.prepare('''SELECT * FROM runr.position''')

    for position in get_position:
        position[2] += position[1]