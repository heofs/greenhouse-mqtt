import time
import psycopg2
import os


class Database():
    """Database connection for PostgreSQL."""

    def __init__(self):
        self.postgres_insert_query = """INSERT INTO sensor_data(device_id,
         temperature, humidity) VALUES (%s,%s,%s) RETURNING *;"""
        db_host = os.getenv('PG_HOST', 'localhost')
        print("Using host: ", db_host)
        try:
            self.connection = psycopg2.connect(user="appuser",
                                               password="87afjn133q4bmaxzcq99",
                                               host=db_host,
                                               port=5432,
                                               database="testdb")
            print("Successfully connected to database...")
        except (Exception, psycopg2.Error) as error:
            print("Failed to establish connection", error)
            raise SystemExit(1)

    def insert_data(self, data):
        """Insert data into database."""
        try:
            device_id = data['device_id']
            temperature = data.get('temperature', None)
            humidity = data.get('humidity', None)
            record_to_insert = (device_id, temperature, humidity)

            self.cursor = self.connection.cursor()
            self.cursor.execute(self.postgres_insert_query, record_to_insert)
            record = self.cursor.fetchall()
            self.connection.commit()

            print("You inserted: ", record)
            return record
        except AttributeError as error:
            print("Attribute missing, Error: ", error)
        except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into table. Error: ", error)
            raise SystemExit(1)

    def close_connection(self):
        """Safely close connection."""
        if(self.connection):
            self.connection.close()
            print("Closed PostgreSQL connection.")
