CREATE KEYSPACE runr WITH replication = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

CREATE TABLE runr.runners (
    runner_id text,
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
    base_speed double,

    PRIMARY KEY (runner_id, base_speed)
);

CREATE TABLE runr.time_elapsed (
    counter_name text,
    time_elapsed counter,
    PRIMARY KEY (counter_name)
);

CREATE TABLE runr.position (
    runner_id text,
    base_speed double,
    location bigint,
    location_exact double,
    starting_position int,
    lat_lng text,
    PRIMARY KEY (runner_id, base_speed)
);

CREATE TABLE runr.trackpoints(
    location_id	int primary key,
    altitude_meters double,
    distance_meters double,
    latitude_degrees double,
    longitude_degrees double
);

CREATE TABLE runr.points_by_distance (
    location_id bigint PRIMARY KEY,
    altitude_meters double,
    distance_meters double,
    latitude_degrees double,
    longitude_degrees double,
);