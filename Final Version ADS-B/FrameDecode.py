# Justin Botton EPHEC 2019

# This class decodes the ADS-B frames

import math
import datetime


class FrameDecode:

    # init FrameDecode
    # @param frame : ADS-B frame to decode
    def __init__(self, frame, position_frame=None):
        if position_frame is not None:
            self.frame_even = frame
            self.frame_odd = position_frame
        self.frame = frame

    def get_frame(self):
        return self.frame

    def get_frame_even(self):
        return self.frame_even

    def get_frame_odd(self):
        return self.frame_odd

    # Integrity

    # check if the frame is consistent
    # @return is_consistent boolean : True if consistent, False if not
    def is_consistent(self):
        frame = self.frame
        generator = "1111111111111010000001001"
        frame_bin = list("{0:048b}".format(int(frame, 16)))
        for i in range(len(frame_bin) - 24):
            if frame_bin[i] == "1":
                for j in range(len(generator)):
                    frame_bin[i + j] = str((int(frame_bin[i + j]) ^ int(generator[j])))
                # end for
            # end if
        # end for
        checksum = ''.join(frame_bin[-24:])
        is_consistent = True
        if checksum != "000000000000000000000000":
            is_consistent = False
        return is_consistent
    # end is_consistent

    # Mode S

    # decode the mode_s in a frame
    # @return mode_s str : Aircraft's mode s transponder value
    def decode_mode_s(self):
        mode_s = str(self.frame[2:8])
        return mode_s
    # end decode_mode_s

    # Type Code

    # decode the frame type code to know which data to extract
    # @return tc int : Frame's Type Code in decimal
    def decode_type_code(self):
        frame = self.frame[8:10]
        binary = "{0:08b}".format(int(frame, 16))
        tc = int(binary[0:5], 2)
        return tc
    # end decode_type_code

    # Name

    # decode the Aircraft's name
    # @return name str : Aircraft's name
    def decode_name(self):
        frame = self.frame[10:22]
        output = ""
        binary = "{0:048b}".format(int(frame, 16))  # parsing the hexa frame to binary
        for i in range(0, 48, 6):
            dec = int(binary[i:i + 6], 2)
            output += self.name_dec2char(dec)
        return output
    # end decode_name

    # dictionnary for decoding Aircraft's name
    # @param dec_number : decimal number
    # @return index[dec_number] char : value corresponding to the given number
    def name_dec2char(self, dec_number):
        index = '#ABCDEFGHIJKLMNOPQRSTUVWXYZ#####_###############0123456789######'
        return index[dec_number]
    # end dec2char

    # Altitude

    # decode the Aircraft's altitude
    # @return altitude float : Aircraft's altitude in meters
    def decode_altitude(self):
        alt, multiple = self.altitude_hex2dec()
        altitude_feet = (alt * multiple) - 1000
        altitude_meters = altitude_feet * 0.3048
        return altitude_meters
    # end decode_altitude

    # parse the hexa altitude part of the frame into decimal
    # @return ouput int : decimal value of the altitude in the frame
    # @return multiple int : 1 if altitude is multiple of 25, 0 if altitude is multiple of 100
    def altitude_hex2dec(self):
        frame = self.frame[10:13]
        multiple = 0
        binary = "{0:4b}".format(int(frame, 16))
        if binary[7] == "1":
            multiple = 25
        elif binary[7] == "0":
            multiple = 25
        binary = binary[:7] + binary[(7 + 1):]
        output = int(binary, 2)
        return output, multiple
    # end altitude_hex2bin

    # Speed

    # decode speed and heading data
    # @return speed_kmh float : Aircraft's speed in km/h
    # @return heading_degrees float : Aircraft's heading in degrees
    # @return heading_compass str : Aircraft's heading on compass
    # @return tilt str : Aircraft's tilt
    # @return vertical_rate float : Aircraft's vertical rate
    def decode_speed_heading(self):
        s_ew, v_ew, s_ns, v_ns, vr_src, s_vr, vr = self.speed_heading_hex2dec()
        v_we = 0
        v_sn = 0
        if s_ew == 0:
            v_we = v_ew - 1
        elif s_ew == 1:
            v_we = -1 * (v_ew - 1)
        if s_ns == 0:
            v_sn = v_ns - 1
        elif s_ns == 1:
            v_sn = -1 * (v_ns - 1)
        speed_kmh = self.speed_calc(v_we, v_sn)
        heading_degrees = self.heading_calc(v_we, v_sn)
        heading_compass = self.direction(heading_degrees)
        tilt = self.tilt(s_vr)
        vertical_rate = ((vr - 1) * 64) / 196.850394
        return speed_kmh, heading_degrees, heading_compass, tilt, vertical_rate
    # end decode_speed_heading

    # parse the hexa speed and heading part of the frame into decimal
    # @return s_ew int : East West velocity sign
    # @return v_ew int : East West velocity
    # @return s_ns int : North South velocity sign
    # @return v_ns int : North South velocity
    # @return vr_src int : vertical rate source
    # @return s_vr int : vertical rate sign
    # @return vr int : vertical rate
    def speed_heading_hex2dec(self):
        frame = self.frame[8:22]
        binary = "{0:048b}".format(int(frame, 16))
        s_ew = int(binary[13], 2)
        v_ew = int(binary[14:24], 2)
        s_ns = int(binary[24], 2)
        v_ns = int(binary[25:35], 2)
        vr_src = binary[35]
        s_vr = binary[36]
        vr = int(binary[37:46], 2)
        return s_ew, v_ew, s_ns, v_ns, vr_src, s_vr, vr
    # end speed_heading_hex2dec

    # calculate the speed in km/h
    # @param v_we int : West East velocity
    # @param v_sn int : South North velocity
    # @return speed_kmh float : Aircraft's speed
    def speed_calc(self, v_we, v_sn):
        v_we = math.pow(v_we, 2)
        v_sn = math.pow(v_sn, 2)
        speed_kt = math.sqrt(v_we + v_sn)
        speed_kmh = speed_kt * 1.852
        return speed_kmh
    # end speed_heading_calc

    # decode Aircraft's tilt
    # @param s_vr : vertical rate sign
    # @return tilt : if the plane goes up or down
    def tilt(self, s_vr):
        tilt = ""
        if s_vr == "1":
            tilt = "DOWN"
        elif s_vr == "0":
            tilt = "UP"
        return tilt
    # end tilt

    # calculate the heading in degrees
    # @param v_we int : West East velocity
    # @param v_sn int : South North velocity
    # @return heading float : Aircraft's heading in degrees
    def heading_calc(self, v_we, v_sn):
        heading = math.atan2(v_we, v_sn) * (360.0 / (2 * math.pi))
        if heading < 0:
            heading = heading + 360.0
        return heading
    # end heading_calc

    # give the point of compass according to the heading in degrees
    # @param heading float : heading in degrees
    # @return direction str : point of compass according to Aircraft heading
    def direction(self, heading):
        if 0 <= heading <= 11.5:
            return "N"
        elif 11.6 <= heading <= 33.75:
            return "NNE"
        elif 33.76 <= heading <= 56.25:
            return "NE"
        elif 56.26 <= heading <= 78.75:
            return "ENE"
        elif 78.76 <= heading <= 101.25:
            return "E"
        elif 101.26 <= heading <= 123.75:
            return "ESE"
        elif 123.76 <= heading <= 146.25:
            return "SE"
        elif 146.26 <= heading <= 168.75:
            return "SSE"
        elif 168.76 <= heading <= 191.25:
            return "S"
        elif 191.26 <= heading <= 213.75:
            return "SSW"
        elif 213.76 <= heading <= 236.25:
            return "SW"
        elif 236.26 <= heading <= 258.75:
            return "WSW"
        elif 258.76 <= heading <= 281.25:
            return "W"
        elif 281.26 <= heading <= 303.75:
            return "WNW"
        elif 303.76 <= heading <= 326.25:
            return "NW"
        elif 326.26 <= heading <= 337.25:
            return "NNW"
        elif 337.26 <= heading <= 360:
            return "N"
    # end direction

    # Position

    def decode_position(self, dict_position, mode_s):
        frame = self
        lat = 0
        lon = 0
        parity = frame.position_parity()
        if mode_s not in dict_position:
            dict_position[mode_s] = {}
        if parity == "0":
            dict_position[mode_s][0] = frame.get_frame()
            dict_position[mode_s]['evenTime'] = datetime.datetime.now()
        elif parity == "1":
            dict_position[mode_s][1] = frame.get_frame()
            dict_position[mode_s]['oddTime'] = datetime.datetime.now()
        if dict_position[mode_s].has_key(0) and dict_position[mode_s].has_key(1) and not dict_position[mode_s].has_key(
                'lat'):
            positions_frames = FrameDecode(dict_position[mode_s][0], dict_position[mode_s][1])
            even_time = dict_position[mode_s]['evenTime']
            odd_time = dict_position[mode_s]['oddTime']
            diff_time = 0
            if even_time > odd_time:
                diff_time = (even_time - odd_time).total_seconds()
            else:
                diff_time = (odd_time - even_time).total_seconds()
            if diff_time < 35:
                lat = positions_frames.latitude()
                lon = positions_frames.longitude(lat)
                dict_position[mode_s]['lat'] = lat
                dict_position[mode_s]['lon'] = lon
        elif dict_position[mode_s].has_key('lat') and dict_position[mode_s].has_key('lon'):
            lat = frame.una_latitude(dict_position[mode_s]['lat'], parity)
            lon = frame.una_longitude(dict_position[mode_s]['lon'], parity, lat)
            dict_position[mode_s]['lat'] = lat
            dict_position[mode_s]['lon'] = lon
        return lat, lon

    def position_parity(self):
        frame = self.frame
        parity = "{0:048b}".format(int(frame, 16))[53]
        return parity

    # parsing hexa frame to get 17 bin numbers and parsing them to get the value
    # @param frame : adsb frame
    # @param coord : if its latitude or longitude
    # @return : latitude / longitude decimal value
    def position_hex2dec(self, frame, coord):
        binary = "{0:036b}".format(int(frame, 16))
        t = binary[0]
        if coord == "lat":
            binary = binary[2:19]
        elif coord == "long":
            binary = binary[19:36]
        output = int(binary, 2)
        return output, t
    # end hex2dec

    # method based on https://github.com/junzis/pyModeS/blob/master/pyModeS/decoder/common.py
    def cpr_n(self, lat, is_odd):
        nl = self.cpr_nl(lat) - is_odd
        if nl > 1:
            return nl
        return 1
    # en cpr_n

    # method based on https://github.com/junzis/pyModeS/blob/master/pyModeS/decoder/common.py
    def cpr_nl(self, lat):
        try:
            nz = 15
            a = 1 - math.cos(math.pi / (2 * nz))
            b = math.cos(math.pi / 180.0 * abs(lat)) ** 2
            nl = 2 * math.pi / (math.acos(1 - a / b))
            NL = math.floor(nl)
            return NL
        except:
            return 1
    # en cprNL

    # Latitude

    # decode the Aircraft's latitude latitude
    def latitude(self):
        even, t0 = self.position_hex2dec(self.frame_even[13:22], "lat")
        odd, t1 = self.position_hex2dec(self.frame_odd[13:22], "lat")
        even = even / 131072.0
        odd = odd / 131072.0
        return self.latitude_calc(even, odd, t0, t1)
    # en latitude

    # calculate the latitude
    # @param latEven_cpr : decimal latitude value from even frame
    # @param latOdd_cpr : decimal latitude vlaue from odd frame
    # @param t0 : time even frame
    # @param t1 : time odd frame
    # @return latitude : Aircraft latitude
    def latitude_calc(self, lateven_cpr, latodd_cpr, t0, t1):
        j = math.floor((59 * lateven_cpr) - (60 * latodd_cpr) + 0.5)
        latitude_even = (360.0 / 60) * (math.fmod(j, 60) + lateven_cpr)
        latitude_odd = (360.0 / 59) * (math.fmod(j, 59) + latodd_cpr)
        if latitude_even >= 270:
            latitude_even = latitude_even - 360
        if latitude_odd >= 270:
            latitude_odd = latitude_odd - 360
        if self.cpr_nl(latitude_even) != self.cpr_nl(latitude_odd):
            return -1.0
        if t0 >= t1:
            return latitude_even
        return latitude_odd, 4
    # end latitude_calc

    # calculate the latitude with the previous one, unambigous latitude
    def una_latitude(self, prev_lat, parity):
        lat_cpr, t = self.position_hex2dec(self.frame[13:22], "lat")
        lat_cpr = lat_cpr / 131072.0
        d_lat = 0
        if parity == "0":
            d_lat = 360.0 / 60.0
        elif parity == "1":
            d_lat = 360.0 / 59.0
        j = math.floor(prev_lat / d_lat) + math.floor((math.fmod(prev_lat, d_lat) / d_lat) - lat_cpr + 0.5)
        latitude = d_lat * (j + lat_cpr)
        return latitude
    # end una_latitude

    # Longitude

    # main call or longitude
    # @param frame_even : ADS-B even frame
    # @param frame_odd : ADS-B odd frame
    # @param latitude : latitude previously calculated
    # @return : Aircraft longitude
    def longitude(self, latitude):
        even, t0 = self.position_hex2dec(self.frame_even[13:22], "long")
        odd, t1 = self.position_hex2dec(self.frame_odd[13:22], "long")
        even = even / 131072.0
        odd = odd / 131072.0
        return self.longitude_calc(even, odd, latitude, t0, t1)
    # en longitude

    # calculate the longitude
    # @param lon_even_cpr : decimal longitude value from even frame
    # @param lon_odd_cpr : decimal longitude value from odd frame
    # @param lat : latitude previously calculated
    # @param t0 : time even frame
    # @param t1 : time odd frame
    def longitude_calc(self, lon_even_cpr, lon_odd_cpr, lat, t0, t1):
        j = math.floor(lon_even_cpr * (self.cpr_nl(lat) - 1) - lon_odd_cpr * self.cpr_nl(lat) + 0.5)
        if t0 >= t1:
            ni = self.cpr_n(lat, 0)
            lon = (360.0 / ni) * (math.fmod(j, ni) + lon_even_cpr)
        else:
            ni = self.cpr_n(lat, 1)
            lon = (360.0 / ni) * (math.fmod(j, ni) + lon_odd_cpr)
        if lon > 180:
            lon = lon - 360
        return lon
    # end longitude_calc

    def una_longitude(self, prev_lon, parity, lat):
        d_lon = 0
        lon_cpr, t = self.position_hex2dec(self.frame[13:22], "long")
        lon_cpr = lon_cpr / 131072.0
        nl_lat = self.cpr_nl(lat)
        if parity == "0":
            if nl_lat > 0:
                d_lon = 360.0 / nl_lat
            elif nl_lat == 0:
                d_lon = 360.0
        elif parity == "1":
            if nl_lat - 1 > 0:
                d_lon = 360.0 / (nl_lat - 1)
            elif nl_lat - 1 == 0:
                d_lon = 360.0
        m = math.floor(prev_lon / d_lon) + math.floor((math.fmod(prev_lon, d_lon) / d_lon) - lon_cpr + 0.5)
        longitude = d_lon * (m + lon_cpr)
        return longitude

# EOF
