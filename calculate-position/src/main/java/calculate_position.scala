
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf
import com.datastax.spark.connector._
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



    var i = 0
    while(true) {
      val start = System.nanoTime
      val runner_positions = sc.cassandraTable("runr", "position")
      val updated_positions = runner_positions.map(x => update_position(x))
      updated_positions.saveToCassandra("runr", "position", SomeColumns("runner_id", "base_speed", "location", "location_exact", "tick"))

      val duration = (System.nanoTime - start) / 1e6

      if(duration < 1000) {
        Thread.sleep((1000 - duration).toLong)
      }
      i = i + 1;
    }
  }
  def update_position(x: CassandraRow) : CassandraRow =
  {
    var position_adjustment = (x.getInt("base_speed") * (.8 + Random.nextDouble() * (1.2 - .8)));
    if (x.getInt("tick") >= x.getInt("starting_position")) {
      var updated_position = new CassandraRow(Array("runner_id", "base_speed", "location", "location_exact", "tick"),
        Array(x.getString("runner_id"),
          x.getDecimal("base_speed").toString(),
          (x.getInt("location_exact") + position_adjustment).toInt.toString(),
          (x.getDouble("location_exact") + position_adjustment).toString(),
          (x.getInt("tick") + 1).toString()))
      return updated_position;

    }
    return x
  }
}