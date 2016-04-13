
import org.apache.spark.SparkContext
import org.apache.spark.SparkConf
import com.datastax.spark.connector._
import com.datastax.spark.connector.cql._
import java.util.Date
import org.apache.spark.rdd.RDD
import scala.util._
import org.apache.spark.broadcast._

object calculate_projected_finish {
  def main(args: Array[String]) {

    val conf = new SparkConf()
      .setMaster("local[4]")
      .setAppName("calculate-projected_finish")
      .set("spark.cassandra.connection.host", "127.0.0.1")



    val sc = new SparkContext(conf)
    val cassandraContext = CassandraConnector(conf)
    var i = 0

    var updated_positions : RDD[CassandraRow] = null

    while(true) {
      val start = System.nanoTime
      val runner_positions = sc.cassandraTable("runr", "runner_tracking")
      runner_positions
        .map(x => project_finish(x))
        .sortBy(_.getDouble("distance_ratio"))
        .zipWithIndex()
        .map(x => new CassandraRow(Array("finish_place", "finish_time", "id"), Array(x._2.toString(), x._1.getString("distance_ratio"), x._1.getString("id"))))
        .saveToCassandra("runr", "projected_finish", SomeColumns("finish_place","finish_time", "id"))

      val duration = (System.nanoTime - start) / 1e6
      if(duration < 30000) {
        Thread.sleep((30000 - duration).toLong)
      }
      updated_positions = null
    }
  }
  def project_finish(x: CassandraRow) : CassandraRow =
  {
      var updated_position = new CassandraRow(Array("id", "distance_ratio"),
        Array(
          x.getString("id"),
          ((38515 - x.getDouble("distance_actual"))/(x.getDouble("average_speed"))).toString()
        ))
      return updated_position;

  }
}