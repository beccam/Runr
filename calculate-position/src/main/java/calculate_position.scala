
import com.datastax.spark.connector.rdd.CassandraTableScanRDD
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf
import com.datastax.spark.connector._
import com.datastax.spark.connector.cql._
import java.util.Date
import org.apache.spark.rdd.RDD
import org.apache.spark.streaming._
import com.datastax.spark.connector.streaming._
import concurrent._
import scala.collection.mutable.ListBuffer
import scala.util._
import scala.math
import org.apache.spark.broadcast._

object position_calculator {
  def main(args: Array[String]) {

    val conf = new SparkConf()
      .setMaster("local[4]")
      .setAppName("calculate-position")
      .set("spark.cassandra.connection.host", "127.0.0.1")



    val sc = new SparkContext(conf)
    val cassandraContext = CassandraConnector(conf)
    var i = 0

    val counters = sc.cassandraTable("runr", "time_elapsed").collect()
    var tick = 0
    if(counters.length > 0)
    {
      tick = counters(0).getInt("time_elapsed")
    }

    val gps_locations = sc.cassandraTable("runr", "points_by_distance").collect().sortBy(_.getInt("location_id"))
    val gps_broadcast = sc.broadcast(gps_locations)

//    val runner_positions = sc.cassandraTable("runr", "runner_tracking")
//
    var updated_positions : RDD[CassandraRow] = null
//    if(tick > 1199) {
//      cassandraContext.withSessionDo(session => session.execute("UPDATE runr.time_elapsed SET time_elapsed = time_elapsed + " + (tick * -1) + " WHERE counter_name='time_elapsed'"))
//      updated_positions = runner_positions.map(x => reset_runners(x, gps_broadcast))
//      tick = 0
//    }
//    else
//    {
//      cassandraContext.withSessionDo(session => session.execute("UPDATE runr.time_elapsed SET time_elapsed = time_elapsed + 1 WHERE counter_name='time_elapsed'"))
//      updated_positions = runner_positions.map(x => update_position(x, gps_broadcast, tick))
//    }
//    updated_positions.cache()
//
//    var prev_positions : RDD[CassandraRow] = null

    while(true) {
      val start = System.nanoTime
      val runner_positions = sc.cassandraTable("runr", "runner_tracking")

      if(tick > 7199 || tick < 0) {
        cassandraContext.withSessionDo(session => session.execute("UPDATE runr.time_elapsed SET time_elapsed = time_elapsed + " + (tick * -1) + " WHERE counter_name='time_elapsed'"))
        updated_positions = runner_positions.map(x => reset_runners(x, gps_broadcast))
      }
      else
      {
        cassandraContext.withSessionDo(session => session.execute("UPDATE runr.time_elapsed SET time_elapsed = time_elapsed + 1 WHERE counter_name='time_elapsed'"))
        updated_positions = runner_positions.map(x => update_position(x, gps_broadcast, tick))
      }


      updated_positions.saveToCassandra("runr", "runner_tracking", SomeColumns("id", "date", "speed", "distance", "distance_actual", "lat_lng", "average_speed"))
//      updated_positions
//        .sortBy(_.getDouble("distance_ratio"))
//        .zipWithIndex()
//        .map(x => new CassandraRow(Array("finish_place", "id"), Array(x._2.toString(), x._1.getString("id"))))
//        .saveToCassandra("runr", "projected_finish", SomeColumns("finish_place","id"))

      val duration = (System.nanoTime - start) / 1e6
      if(duration < 1000) {
        Thread.sleep((1000 - duration).toLong)
      }
      tick = tick + 1;
      updated_positions = null
    }
  }
  def update_position(x: CassandraRow, gps_locations: Broadcast[Array[CassandraRow]], tick: Int) : CassandraRow =
  {
    val position_adjustment = (x.getDouble("speed").toInt * (.8 + Random.nextDouble() * (1.2 - .8)));
    if (tick >= x.getInt("starting_position") && (x.getDouble("distance_actual").toInt + position_adjustment).toInt < gps_locations.value.length) {
        var location = gps_locations.value((x.getDouble("distance_actual").toInt + position_adjustment).toInt)
        var updated_position = new CassandraRow(Array("id", "date", "speed", "distance", "distance_actual", "lat_lng", "average_speed", "distance_ratio", "starting_position"),
          Array(x.getString("id"),
            new Date(),
            x.getDecimal("speed").toString(),
            (x.getDouble("distance_actual") + position_adjustment).toInt.toString(),
            (x.getDouble("distance_actual") + position_adjustment).toString(),
            (location.getString("latitude_degrees") + "," + location.getString("longitude_degrees")),
            (((x.getDouble("average_speed") + (position_adjustment / 1.5)) / 2).toString()),
            ((38515 - (x.getDouble("distance_actual") + position_adjustment))/((x.getDouble("average_speed") + (position_adjustment)) / 2)).toString(),
            x.getInt("starting_position").toString()))
        return updated_position;
    }
    else
    {

      var updated_position = new CassandraRow(Array("id", "date", "speed", "distance", "distance_actual", "lat_lng", "average_speed", "distance_ratio", "starting_position"),
        Array(x.getString("id"),
          new Date(),
          x.getDecimal("speed").toString(),
          (x.getDouble("distance_actual").toInt).toString(),
          (x.getDouble("distance_actual")).toString(),
          (x.getString("lat_lng")),
          (x.getDouble("average_speed").toString()),
          ((38515 - (x.getDouble("distance_actual") + position_adjustment))/((x.getDouble("average_speed") + (position_adjustment)) / 2)).toString(),
          x.getInt("starting_position").toString()))
      return updated_position;
    }
  }
  def reset_runners(x: CassandraRow, gps_locations: Broadcast[Array[CassandraRow]]) : CassandraRow = {
    var updated_position = new CassandraRow(Array("id", "date", "speed", "distance", "distance_actual", "lat_lng", "average_speed", "starting_position"),
      Array(x.getString("id"),
        new Date(),
        x.getDecimal("speed").toString(),
        "0",
        "0",
        gps_locations.value(0).getString("latitude_degrees") + "," + gps_locations.value(0).getString("longitude_degrees"),
        x.getDecimal("speed").toString(),
        x.getInt("starting_position").toString()))
    return updated_position;
  }
}