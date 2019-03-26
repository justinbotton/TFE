# Justin Botton EPHEC 2019

import sqlite3 as lite
import sys
from datetime import datetime


class OrmSqlite:

    def __init__(self, database_path):
        self.connection = ""
        self.cursor = ""
        try:
            self.connection = lite.connect(database_path)
            self.cursor = self.connection.cursor()
        except lite.Error, e:
            sys.exit(1)

    def get_cursor(self):
        return self.cursor

    def get_connection(self):
        return self.connection

    def insert_into_last_flight_name(self, mode_s, last_flight_name):
        with self.get_connection():
            query = "UPDATE tb_Aircraft SET lastFlightName='"+last_flight_name+"' WHERE modeS='"+mode_s+"'"
            self.get_cursor().execute(query)

    def insert_into_speed_heading(self, mode_s, speed, heading_degrees, heading_compass, tilt):
        with self.get_connection():
            time = str(datetime.now())
            query_speed = "INSERT INTO tb_Vitesse VALUES('"+time+"', '"+mode_s+"', "+str(speed)+", "+str(heading_degrees)+", '"+str(heading_compass)+"', '"+str(tilt)+"')"
            self.get_cursor().execute(query_speed)

    def inssert_into_position(self, mode_s, altitude, latitude, longitude):
        with self.get_connection():
            time = str(datetime.now())
            query_position = "INSERT INTO tb_Vitesse VALUES('"+time+"', '"+mode_s+"', "+str(altitude)+", "+str(latitude)+", "+str(longitude)+")"
            self.get_cursor().execute(query_position)
# EOF
