CREATE KEYSPACE runr WITH replication = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

CREATE TABLE runr.runner_predictions (
    id text,
    date timestamp,
    finish_place int,
    finish_time double,
    PRIMARY KEY (id, date)
) WITH CLUSTERING ORDER BY (date DESC);

CREATE TABLE runr.runner_tracking (
    id text,
    date timestamp,
    lat_lng text,
    distance bigint,
    distance_actual double,
    starting_position int,
    speed double,
    average_speed double,
    PRIMARY KEY (id)
);

CREATE TABLE runr.runner_tracking_history (
    id text,
    date timestamp,
    lat_lng text,
    distance bigint,
    distance_actual double,
    starting_position int,
    speed double,
    average_speed double,
    PRIMARY KEY (id, date)
) WITH CLUSTERING ORDER BY (date DESC);

CREATE TABLE runr.runners (
    id text PRIMARY KEY,
    first_name text,
    last_name text,
    given_name text,
    birth_country text,
    birth_state text,
    birth_city text,
    birth_year int,
    birth_month int,
    birth_day int,
    weight int,
    height int,
    cluster int,
    cluster_dist double,
    given_name_id text
);

CREATE TABLE runr.projected_finish (
    finish_place int PRIMARY KEY,
    id text,
    finish_time double,
    speed double,
);

CREATE TABLE runr.cluster_details (
    cluster int,
    mile int,
    runners int,
    PRIMARY KEY (cluster, mile)
) WITH CLUSTERING ORDER BY (mile ASC);

CREATE TABLE runr.points_by_distance (
    location_id bigint PRIMARY KEY,
    altitude_meters double,
    distance_meters double,
    latitude_degrees double,
    longitude_degrees double,
);

CREATE TABLE runr.points_by_distance_filtered (
    location_id bigint,
    altitude_meters double,
    distance_meters double ,
    latitude_degrees double,
    longitude_degrees double,
    PRIMARY KEY ((distance_meters), location_id)
) WITH CLUSTERING ORDER BY (location_id DESC);

CREATE TABLE runr.cluster_summary (
    cluster int PRIMARY KEY,
    runners int,
    avg_speed double,
    min_speed double,
    max_speed double,
    std_deviation double,
);

CREATE TABLE runr.time_elapsed (
    counter_name text,
    time_elapsed counter,
    PRIMARY KEY (counter_name)
);


