
//lazy val root = (project in file(".")).
//  settings(
    name := "calculate_kmeans_cluster"
    version := "1.0"
    scalaVersion := "2.10.5"
    mainClass in Compile := Some("calculate_kmeans_cluster")
//  )

libraryDependencies ++= Seq(
  "org.apache.spark" % "spark-core_2.10" % "1.6.0" % Provided,
  "org.apache.spark" % "spark-mllib_2.10" % "1.6.0" % Provided,
  "com.datastax.spark" % "spark-cassandra-connector_2.10" % "1.6.0-M1"
)
//mergeStrategy in assembly <<= (mergeStrategy in assembly) { (old) =>
//{
//  case PathList("javax", "servlet", xs @ _*) => MergeStrategy.last
//  case PathList("org", "apache", xs @ _*) => MergeStrategy.last
//  case PathList("com", "google", xs @ _*) => MergeStrategy.last
//  case PathList("com", "esotericsoftware", xs @ _*) => MergeStrategy.last
//  case PathList("javax", "xml", xs @ _*) => MergeStrategy.last
//  case PathList("io", "netty", xs @ _*) => MergeStrategy.last
//  case x if x.startsWith("META-INF/io.netty.versions.properties") => MergeStrategy.last
//  case "about.html" => MergeStrategy.rename
//  case x => old(x)
//}
//}


