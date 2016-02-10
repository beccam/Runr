
import com.datastax.spark.connector.rdd.CassandraTableScanRDD
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf
import com.datastax.spark.connector._
import com.datastax.spark.connector.cql._
import org.apache.spark.streaming._
import com.datastax.spark.connector.streaming._
import concurrent._
import scala.util._
import scala.math

object position_calculator {
  def main(args: Array[String]) {

    val conf = new SparkConf()
      .setMaster("local[4]")
      .setAppName("calculate-position")
      .set("spark.cassandra.connection.host", "127.0.0.1")



    val sc = new SparkContext(conf)
    val cassandraContext = CassandraConnector(conf)

    var i = 0
    val gps_locations = sc.cassandraTable("runr", "points_by_distance").collect()
    while(true) {
      val start = System.nanoTime

      val counters = sc.cassandraTable("runr", "time_elapsed").collect()

      cassandraContext.withSessionDo(session => session.execute("UPDATE runr.time_elapsed SET time_elapsed = time_elapsed + 1 WHERE counter_name='time_elapsed'"))
      var tick = 0
      if(counters.length > 0)
      {
        tick = counters(0).getInt("time_elapsed")
      }
      val runner_positions = sc.cassandraTable("runr", "position")
      val updated_positions = runner_positions.map(x => update_position(x, gps_locations,tick))
      updated_positions.saveToCassandra("runr", "position", SomeColumns("runner_id", "base_speed", "location", "location_exact", "lat_lng"))

      val duration = (System.nanoTime - start) / 1e6

      if(duration < 1000) {
        Thread.sleep((1000 - duration).toLong)
      }
      i = i + 1;
    }
  }
  def update_position(x: CassandraRow, gps_locations: Array[CassandraRow], tick: Int) : CassandraRow =
  {
    var position_adjustment = (x.getInt("base_speed") * (.8 + Random.nextDouble() * (1.2 - .8)));
    if (tick >= x.getInt("starting_position") && (x.getInt("location_exact") + position_adjustment).toInt < gps_locations.length) {
        var location = gps_locations((x.getInt("location_exact") + position_adjustment).toInt)
        var updated_position = new CassandraRow(Array("runner_id", "base_speed", "location", "location_exact", "lat_lng"),
          Array(x.getString("runner_id"),
            x.getDecimal("base_speed").toString(),
            (x.getInt("location_exact") + position_adjustment).toInt.toString(),
            (x.getDouble("location_exact") + position_adjustment).toString(),
            (location.getString("latitude_degrees") + "," + location.getString("longitude_degrees"))))
        return updated_position;
    }
    else
    {

      var updated_position = new CassandraRow(Array("runner_id", "base_speed", "location", "location_exact", "lat_lng"),
        Array(x.getString("runner_id"),
          x.getDecimal("base_speed").toString(),
          (x.getInt("location_exact")).toString(),
          (x.getDouble("location_exact")).toString(),
          (x.getString("lat_lng"))))
      return updated_position;
    }
  }
}