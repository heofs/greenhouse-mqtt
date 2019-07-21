CREATE ROLE appuser WITH PASSWORD '87afjn133q4bmaxzcq99' CREATEDB LOGIN INHERIT;
CREATE DATABASE testdb;
GRANT ALL PRIVILEGES ON DATABASE testdb TO appuser;

\c testdb

CREATE TABLE public.sensor_data(
    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    device_id TEXT NOT NULL,
    location TEXT,
    temperature FLOAT(1),
    humidity FLOAT(1)
);
SELECT create_hypertable('public.sensor_data', 'created');
-- GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.sensor_data TO appuser;

-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO appuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public to appuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public to appuser;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public to appuser;

CREATE ROLE grafanareader WITH PASSWORD 'grafana435623512364' LOGIN;
-- GRANT USAGE ON ALL TABLES IN SCHEMA public TO grafanareader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafanareader;