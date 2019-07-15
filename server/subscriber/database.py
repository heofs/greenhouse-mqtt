import time
import psycopg2
import os


class Database():
    """Database connection for PostgreSQL."""

    def __init__(self):

        self.postgres_insert_query = """INSERT INTO sensor_data(device_id,
         temperature, humidity) VALUES (%s,%s,%s) RETURNING *;"""

        try:
            self.connection = psycopg2.connect(user="henning",
                                               password="password",
                                               host=os.getenv(
                                                   'PG_HOST', 'localhost'),
                                               port=5432,
                                               database="testdb")
            print("Initialized database...")
        except (Exception, psycopg2.Error) as error:
            print("Failed to establish connection", error)

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
        except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into table. Error: ", error)
        except AttributeError as error:
            print("Attribute missing, Error: ", error)

    def close_connection(self):
        """Safely close connection."""
        if(self.connection):
            self.connection.close()
            print("Closed PostgreSQL connection.")
