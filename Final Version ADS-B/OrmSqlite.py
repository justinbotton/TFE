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

    def insert_into_mode_s(self, mode_s):
        with self.get_connection():
            query_mode_s = "INSERT INTO tb_Aircraft(mode_s) SELECT '"+mode_s+"' WHERE NOT EXISTS(SELECT mode_s FROM tb_Aircraft WHERE tb_Aircraft.mode_s = '"+mode_s+"')"
            self.get_cursor().execute(query_mode_s)

    def update_last_flight_name(self, mode_s, last_flight_name):
        with self.get_connection():
            query_last_flight_name = "UPDATE tb_Aircraft SET last_flight_name='"+last_flight_name+"' WHERE mode_s='"+mode_s+"'"
            self.get_cursor().execute(query_last_flight_name)

    def insert_into_speed_heading(self, mode_s, speed, heading_degrees, heading_compass, tilt, vertical_rate):
        with self.get_connection():
            time = str(datetime.now())
            query_speed_heading = "INSERT INTO tb_Speed_Heading VALUES('"+time+"', '"+mode_s+"', "+str(speed)+", "+str(heading_degrees)+", '"+str(heading_compass)+"', '"+str(tilt)+"', '"+str(vertical_rate)+"')"
            self.get_cursor().execute(query_speed_heading)

    def insert_into_position(self, mode_s, altitude, latitude, longitude):
        with self.get_connection():
            time = str(datetime.now())
            query_position = "INSERT INTO tb_Position VALUES('"+time+"', '"+mode_s+"', "+str(altitude)+", "+str(latitude)+", "+str(longitude)+")"
            self.get_cursor().execute(query_position)
# EOF
