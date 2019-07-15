import time
import psycopg2

try:
    connection = psycopg2.connect(user="henning",
                                  password="password",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="testdb")
    cursor = connection.cursor()
    postgres_insert_query = """INSERT INTO sensor_data(device_id, temperature, humidity) VALUES (%s,%s,%s) RETURNING *;"""
    for x in range(5):
        record_to_insert = ('deviceId1235', x, x)
        cursor.execute(postgres_insert_query, record_to_insert)
        connection.commit()
        record = cursor.fetchall()
        print("You inserted - ", record)
        time.sleep(3)
except (Exception, psycopg2.Error) as error:
    if(connection):
        print("Failed to insert record into sensor data table", error)
except KeyboardInterrupt:
    print("Shutting down!")
    break
finally:
    # closing database connection.
    if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")


# counter = 1
# while True:
#     print(f"Running app: {counter}", flush=True)
#     counter += 1
#     time.sleep(1)
