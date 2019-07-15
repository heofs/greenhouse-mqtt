import time
from database import Database
from subscriber import Server


if __name__ == '__main__':
    try:
        db = Database()
        server = Server(callback=db.insert_data)
        server.run()
    except KeyboardInterrupt:
        db.close_connection()
        print("Shutting down...")
