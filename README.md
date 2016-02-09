# Runr Demo

Navigate to the cql folder
```

```

Load the schema
```
cd ../cql
cqlsh -f runr.cql
```

Load the Solr cores
```
cd ../solr
dsetool create_cors schema=runr_schema.xml solrconfig=solrconfig.xml
```

Load the data
```
cd ../data-loader
python load_positions.py
python load_runners.py
```

Run the Web Interface
```
cd ../web
./run
```

Build and start the submit the spark job
```
cd ../calculate-position
sbt package
dse spark-submit --class position_calculator target/scala-2.10/calculate-position_2.10-1.0.jar
```
