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

CREATE TABLE runr.position (
    runner_id text,
    base_speed double,
    location int,
    PRIMARY KEY (runner_id, base_speed)
);