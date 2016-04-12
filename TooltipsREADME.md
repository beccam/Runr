## Logo Tooltip - DSE Runr Application
DSE Runr is a sample cloud application built for tracking runners in a marathon. Different parts of this app will show how a cloud application can leverage DataStax Enterprise as the data management layer of choice.

## Clock Tooltip - DSE Analytics race simulation
The clock represents the race time from when the simulation began. On the backend of the cloud app, there is a recurring DSE Analytics job occuring that simulates just over 10,000 runners moving along the race course. Every second the runners location is updated based on an algorithm that determines their pace.

## Searchbar Tooltip - DSE Search 
Being able to search data is a key component of a cloud application. DSE Search enables users to search for runners using type ahead functionality. 

## Runner Data Tooltip - DSE Core and DSE Analytics
Here the user can see basic information about the runner they have selected, being powered by standard transactional queries of DSE Core (Cassandra). An example is `SELECT cluster,weight, height, birth_year, birth_month, birth_day FROM runr.runners`.  
The DSE Analytics Spark job for the simulation can be found [here](https://github.com/datastax-demos/Runr/blob/master/calculate-position/src/main/java/calculate_position.scala). 

## Clustering Tooltip - DSE Search
Runners are tracked along the race course by these circular "Runner Clusters." The number inside the cluster designates how many runners are in that section of the race. As the map zooms in/out the number of clusters changes, as does the count of runners in each one. This number of runners is powered by a DSE Search geospatial query, as seen in [here](https://github.com/datastax-demos/Runr/blob/master/web/routes/index.py) at line 233.
