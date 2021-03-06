# Justin Botton EPHEC 2019

# Create the Aircraft object and decode the datas


class Aircraft:

    # init Aircraft
    # @param mode_s str : Aircraft's transponder value
    # @param last_flight_name str : Aircraft's name
    # @param speed float : Aircraft's speed
    # @param heading_degrees float : Aircraft's heading in degrees
    # @param heading_compass str : Aircraft's heading on compass
    # @param direction str : Aircraft's direction according to points of compass
    # @param tilt str : Aircraft's tilt, up or down
    # @param vertical_rate float : Aircraft's vertical rate
    # @param altitude float : Aircraft's altitude
    # @param latitude float : Aircraft's latitude
    # @param longitude float : Aircraft's longitude
    def __init__(self, mode_s, last_flight_name, speed, heading_degrees, heading_compass, tilt, vertical_rate, altitude, latitude, longitude):
        self.mode_s = mode_s
        self.last_flight_name = last_flight_name
        self.speed = speed
        self.heading_degrees = heading_degrees
        self.heading_compass = heading_compass
        self.tilt = tilt
        self.vertical_rate = vertical_rate
        self.altitude = altitude
        self.latitude = latitude
        self.longitude = longitude
    # end __init__

    # Getters

    # get the modeS value of self
    def get_mode_s(self):
        return self.mode_s

    # get the name value of self
    def get_last_flight_name(self):
        return self.last_flight_name

    # get the speed value of self
    def get_speed(self):
        return self.speed

    # get the heading_degrees value of self
    def get_heading_degrees(self):
        return self.heading_degrees

    # get the heading_compass value of self
    def get_heading_compass(self):
        return self.heading_compass

    # get the tilt value of self
    def get_tilt(self):
        return self.tilt

    #get the vertical rate of self
    def get_vertical_rate(self):
        return self.vertical_rate

    # get the altitude value of self
    def get_altitude(self):
        return self.altitude

    # get the latitude value of self
    def get_latitude(self):
        return self.latitude

    # get the longitude value of self
    def get_longitude(self):
        return self.longitude

    # Setters

    # set the modeS of self
    def set_mode_s(self, mode_s):
        self.mode_s = mode_s

    # set the name of self
    def set_last_flight_name(self, last_flight_name):
        self.last_flight_name = last_flight_name

    # set the speed of self
    def set_speed(self, speed):
        self.speed.append(speed)

    # set the heading_degrees of self
    def set_heading_degrees(self, heading_degrees):
        self.heading_degrees.append(heading_degrees)

    # set the heading_compass of self
    def set_heading_compass(self, heading_compass):
        self.heading_compass.append(heading_compass)

    # set the tilt of self
    def set_tilt(self, tilt):
        self.tilt.append(tilt)

    # set the vertical rate of self
    def set_vertical_rate(self, vertical_rate):
        self.vertical_rate.append(vertical_rate)

    # set the altitude of self
    def set_altitude(self, altitude):
        self.altitude.append(altitude)

    # set the latitude of self
    def set_latitude(self, latitude):
        self.latitude.append(latitude)

    # set the longitude of self
    def set_longitude(self, longitude):
        self.longitude.append(longitude)


# EOF
