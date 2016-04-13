import org.apache.spark.SparkContext
import org.apache.spark.SparkConf
import com.datastax.spark.connector._
import org.apache.spark.sql.SaveMode
import org.apache.spark.sql.cassandra.CassandraSQLContext
import org.apache.spark.sql.cassandra._
import org.apache.spark.sql
import com.datastax.spark.connector.cql._
import java.util.Date
import org.apache.spark.rdd.RDD
import scala.util._
import org.apache.spark.ml.feature.VectorAssembler
import org.apache.spark.ml.clustering.KMeans

object calculate_kmeans_cluster {
  def main(args: Array[String]) {

    val conf = new SparkConf()
      .setMaster("local[4]")
      .setAppName("cluster_calculation")
      .set("spark.cassandra.connection.host", "127.0.0.1")



    val sc = new SparkContext(conf)
    val cassandraContext = CassandraConnector(conf)
    val csc = new CassandraSQLContext(sc)

    val results = csc.sql("SELECT id, height, weight, age from runr.runners")

    val assembler = new VectorAssembler().setInputCols(Array("height", "weight", "age")).setOutputCol("features")


    val dataset = assembler.transform(results)

    val kmeans = new KMeans().setK(11).setFeaturesCol("features").setPredictionCol("cluster")


    val model = kmeans.fit(dataset)
    val predictions = model.transform(dataset).select("id", "cluster")
//    predictions.saveToCassandra("runr", "runners", SomeColumns("id", "cluster"))

    val rows = results.collect()
    predictions.foreach(println)
    //results.write.format("org.apache.spark.sql.cassandra").options(table="test", keyspace = "runr").save(mode ="append")
    //results.saveToCassandra("runr", "test")

//    results.registerTempTable("scored_results")
////    csc.sql("insert into table runr.test select * from scored_results")
//
    predictions.write.format("org.apache.spark.sql.cassandra")
      .mode(SaveMode.Append)
      .options(Map("keyspace" -> "runr", "table" -> "runners"))
      .save()

  }
}
