# Justin Botton EPHEC 2019

import sqlite3 as lite
import sys
from datetime import datetime

# This class is used to create a connection to a database base on a path to the database file
# and has some routines to interact with the database


class OrmSqlite:

    # init OrmSqlite : create the connection to the database_path
    # @param database_path : path to the database file
    def __init__(self, database_path):
        self.connection = ""
        self.cursor = ""
        try:
            self.connection = lite.connect(database_path)
            self.cursor = self.connection.cursor()
        except lite.Error, e:
            sys.exit(1)
    # end __init__

    # Getters

    # get cursor of self
    def get_cursor(self):
        return self.cursor

    # get connection of self
    def get_connection(self):
        return self.connection

    # Update

    # update the flight name of the mode_s Aircraft
    # @param mode_s str : Aircraft's mode_s transponder value
    # @param last_flight_name str : Aircraft's flight name
    def update_last_flight_name(self, mode_s, last_flight_name):
        with self.get_connection():
            query_last_flight_name = "UPDATE tb_Aircraft SET lastFlightName='"+last_flight_name+"' WHERE modeS='"+mode_s+"'"
            self.get_cursor().execute(query_last_flight_name)
    # end update_last_flight_name

    # Insert Into

    # insert speed, heading_degrees, heading_compass and tilt into tb_Speed_Heading
    # @param mode_s str : Aircraft's mode_s transponder value
    # @param speed float : Aircraft's speed in km/h
    # @param heading_degrees float : Aircraft's heading in degrees
    # @param heading_compass str : Aircraft's heading on compass
    # @param tilt str : Aircraft's tilt
    def insert_into_speed_heading(self, mode_s, speed, heading_degrees, heading_compass, tilt):
        with self.get_connection():
            time = str(datetime.now())
            query_speed = "INSERT INTO tb_Speed_Heading VALUES('"+time+"', '"+mode_s+"', "+str(speed)+", "+str(heading_degrees)+", '"+str(heading_compass)+"', '"+str(tilt)+"')"
            self.get_cursor().execute(query_speed)
    # end insert_into_speed_heading

    # insert altitude, latitude and longitude into tb_Position
    # @param mode_s str : Aircraft's mode_s transponder value
    # @param altitude float : Aircraft's altitude
    # @param latitude float : Aircraft's latitude
    # @param longitude float : Aircraft's longitude
    def insert_into_position(self, mode_s, altitude, latitude, longitude):
        with self.get_connection():
            time = str(datetime.now())
            query_position = "INSERT INTO tb_Position VALUES('"+time+"', '"+mode_s+"', "+str(altitude)+", "+str(latitude)+", "+str(longitude)+")"
            self.get_cursor().execute(query_position)
    # end insert_into_position


# EOF
