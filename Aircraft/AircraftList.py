# Justin Botton EPHEC 2019

import sys
from FrameDecode import FrameDecode
from Aircraft import Aircraft
from OrmSqlite import OrmSqlite

# This class keeps a list of all Aircraft's data


class AircraftList:

    # init AircraftList
    def __init__(self):
        self.dict = {}
    # end __init__

    # add an Aircraft to the dict of self
    # @param mode_s str : Aircraft's mode_s transponder value
    def add_aircraft(self, mode_s):
        self.dict[mode_s] = Aircraft("", "", [], [], [], [], [], [], [])
    # end __init__

    # Getters

    # get the dict of self
    def get_dict(self):
        return self.dict

    # get the dict of the mode_s Aircraft
    # @param mode_s str : Aircraft's mode_s transponder value
    def get_dict_aircraft(self, mode_s):
        return self.dict[mode_s]

    # get the speed of the mode_s Aircraft in dict of self
    # @param mode_s str : Aircraft's mode_s transponder value
    def get_dict_speed(self, mode_s):
        return self.dict[mode_s].get_speed()

    # get the last_flight_name of the mode_s Aircraft in dict of self
    # @param mode_s str : Aircraft's mode_s transponder value
    def get_dict_last_flight_name(self, mode_s):
        return self.dict[mode_s].get_last_flight_name()

    # get the heading_degrees of the mode_s Aircraft in dict of self
    # @param mode_s str : Aircraft's mode_s transponder value
    def get_dict_heading_degrees(self, mode_s):
        return self.dict[mode_s].get_heading_degrees()

    # get the heading_compass of the mode_s Aircraft in dict of self
    # @param mode_s str : Aircraft's mode_s transponder value
    def get_dict_heading_compass(self, mode_s):
        return self.dict[mode_s].get_heading_compass()

    # get the tilt of the mode_s Aircraft in dict of self
    # @param mode_s str : Aircraft's mode_s transponder value
    def get_dict_tilt(self, mode_s):
        return self.dict[mode_s].get_tilt()

    # get the altitude of the mode_s Aircraft in dict of self
    # @param mode_s str : Aircraft's mode_s transponder value
    def get_dict_altitude(self, mode_s):
        return self.dict[mode_s].get_altitude()

    # get the latitude of the mode_s Aircraft in dict of self
    # @param mode_s str : Aircraft's mode_s transponder value
    def get_dict_latitude(self, mode_s):
        return self.dict[mode_s].get_latitude()

    # get the longitude of the mode_s Aircraft in dict of self
    # @param mode_s str : Aircraft's mode_s transponder value
    def get_dict_longitude(self, mode_s):
        return self.dict[mode_s].get_longitude()

    # Setters

    # set the speed, heading, direction and tilt of the mode_s Aircraft in dict of self
    # @param mode_s str : Aircraft's mode_s transponder value
    # @param speed float : Aircraft's speed in km/h
    # @param heading float : Aircraft's heading in degrees
    # @param direction str : Aircraft's direction on compass
    # @param tilt str : Aircraft's tilt
    def set_speed_in_dict(self, mode_s, speed, heading, direction, tilt):
        self.dict[mode_s].set_speed(speed)
        self.dict[mode_s].set_heading_degrees(heading)
        self.dict[mode_s].set_heading_compass(direction)
        self.dict[mode_s].set_tilt(tilt)

    # set the last_flight_name of the mode_s Aircraft in dict of self
    # @param last_flight_name str : Aircraft's flight name
    def set_last_flight_name_in_dict(self, mode_s, last_flight_name):
        self.dict[mode_s].set_last_flight_name(last_flight_name)

    # set the altitude of the mode_s Aircraft in dict of self
    # @param mode_s str : Aircraft's mode_s transponder value
    # @param altitude float : Aircraft's altitude in meters
    def set_altitude_in_dict(self, mode_s, altitude):
        self.dict[mode_s].set_altitude(altitude)

    # set the latitude and longitude of the mode_s Aircraft in dict of self
    # @param latitude float : Aircraft's latitude
    # @param longitude float : Aircraft's longitude
    def set_latitude_and_longitude(self, mode_s, latitude, longitude):
        self.dict[mode_s].set_latitude(latitude)
        self.dict[mode_s].set_longitude(longitude)

# end AircraftList


# main execution

aircraft_dict = AircraftList()
dict_position = {}
database = OrmSqlite("/var/www/html/database/adsb-dev")

while True:
    line = sys.stdin.readline()
    if line.startswith("*8d"):
        frame = FrameDecode(line[1:29])
        if frame.is_consistent():
            type_code = frame.decode_type_code()
            mode_s = frame.decode_mode_s()
            if not aircraft_dict.get_dict().has_key(mode_s):
                aircraft_dict.add_aircraft(mode_s)
            if type_code == 19:
                speed, heading, direction, tilt = frame.decode_speed_heading()
                aircraft_dict.set_speed_in_dict(mode_s, speed, heading, direction, tilt)
                database.insert_into_speed_heading(mode_s, speed, heading, direction, tilt)
            elif 9 <= type_code <= 18:
                altitude = frame.decode_altitude()
                aircraft_dict.set_altitude_in_dict(mode_s, altitude)
                latitude, longitude = frame.decode_position(dict_position, mode_s)
                aircraft_dict.set_latitude_and_longitude(mode_s, latitude, longitude)
                database.insert_into_position(mode_s, altitude, latitude, longitude)
            elif 1 <= type_code <= 4:
                last_flight_name = frame.decode_last_flight_name()
                aircraft_dict.set_last_flight_name_in_dict(mode_s, last_flight_name)
                database.update_last_flight_name(mode_s, last_flight_name)


# EOF
