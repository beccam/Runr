
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf
import com.datastax.spark.connector._
import org.apache.spark.streaming._
import com.datastax.spark.connector.streaming._
import concurrent._

object position_calculator {
  def main(args: Array[String]) {

    val conf = new SparkConf()
      .setMaster("local[2]")
      .setAppName("calculate-position")
      .set("spark.cassandra.connection.host", "127.0.0.1")



    val sc = new SparkContext(conf)

    var i = 0
    while(i < 5) {
      val start = System.nanoTime
      val runner_positions = sc.cassandraTable("runr", "position")
      val updated_positions = runner_positions.map(x => new CassandraRow(Array("runner_id", "base_speed", "location"), Array(x.getString("runner_id"), x.getDecimal("base_speed").toString(), (x.getInt("location") + x.getInt("base_speed")).toString())))
      updated_positions.saveToCassandra("runr", "position", SomeColumns("runner_id", "base_speed", "location"))

      val duration = (System.nanoTime - start) / 1e6
      if(duration < 1000) {
        Thread.sleep((1000 - duration).toLong)
      }
      i = i + 1;
    }
  }
}