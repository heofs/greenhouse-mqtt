import time
from database import Database
from subscriber import Server


if __name__ == '__main__':
    try:
        print("----------------- starting subscriber -----------------")
        db = Database()
        server = Server(callback=db.insert_data)
        server.run()
    except KeyboardInterrupt:
        db.close_connection()
        print("----------------- stopping subscriber -----------------")
