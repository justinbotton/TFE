#! /usr/bin/env python3
"""
bistatic_dopper.py

This module provides classes and functions to determine the double Doppler
shift for a bistatic radar.

The incident and reflected wave travels on a slanted plan from the transmitter,
T, at one focus of an ellipse to the meteor, M, on the ellipse, then on to the
receiver, R, at the second focus.

The radial velocities of M relative to T and R produce a shift in the observed
frequency.

written by Michel Anciaux, 26-Mar-2019
"""
import numpy as np
from numpy import sin, cos, sqrt, deg2rad
import datetime as dt
import scipy.constants as constants

C0 = constants.c
# Earth
# equatorial radius WGS-84
Ra = 6378.1370e3
# polar radius
Rb = 6356.7523142e3
# eccentricity
ecc = sqrt(1 - (Rb / Ra)**2)

# altitude range
hmin = 80e3
hmax = 100e3


# the slanted height, hl, (distance from M to the axis T-R)
def hslant(h, R):
    return sqrt(h**2 + 2 * R * h)

# maximum slant height, meteor at horizon
# hlmax = hslant(hmax, Re)


def geodeticToECEF(lat, lon, h=0):
    '''
      Convert from geodetic to Earth centred Eart fixed coordinates.
      N is the prime vertical radius of curvature

      lat: latitude (rad)
      lon: longitude (rad)
      h:   altitude (m)
      return: ECEF coordinates (m)
    '''
    N = Ra / sqrt(1 - (ecc * sin(lat))**2)
    # print("N: ", N)
    x = (N + h) * cos(lat) * cos(lon)
    y = (N + h) * cos(lat) * sin(lon)
    z = ((Rb / Ra)**2 * N + h) * sin(lat)
    return np.array([x, y, z])


def ENUtoECEF(penu, lon, lat, pecef_origin=np.array((0, 0, 0))):
    '''
        Convert from local tangent plane (East-North-Up) to ECEF coordinates.
        penu: np.array(x, y, z) in ENU system (m)
        lon: latitude of local ENU origin (rad)
        lat: longitude of local ENU origin (rad)
        pecef_origin: np.array(ECEF coordinates) of local ENU origin (m)
        return: ECEF coordinates (m)

        To convert a velocity vector, leave out the pecef_origin)
    '''
    M = np.array([(-sin(lon), -sin(lat) * cos(lon), cos(lat) * cos(lon)),
                  (cos(lon), -sin(lat) * sin(lon), cos(lat) * sin(lon)),
                  (0, cos(lat), sin(lat))])
    return M.dot(penu) + pecef_origin


class GeoPos():
    ''' Position as Earth centred coordinates
        longitude and latitude in degrees, height in meters
        ground_speed in m/s, azimuth in degrees
        (North=0, positive Eastward)
    '''

    def __init__(self, latitude, longitude, height=0, name=None,
                 ground_speed=0, azimuth=0):
        lon = deg2rad(longitude)
        lat = deg2rad(latitude)
        self.lon = lon
        self.lat = lat
        self.pos = geodeticToECEF(lat, lon, height)
        self.name = name
        self.vel = None
        if azimuth:
            az = deg2rad(azimuth)
            if ground_speed:
                venu = ground_speed * np.array((sin(az), cos(az), 0.0))
                self.vel = ENUtoECEF(venu, lon, lat)
        # print(self)

    def get_name(self):
        return self.name

    def get_lat(self):
        return self.lat

    def get_lon(self):
        return self.lon

    def get_pos(self):
        return self.pos

    def dist(self, to_geopos):
        '''
            computes the distance to another another geopos
        '''
        return sqrt(((self.pos - to_geopos.pos)**2).sum())

    def unit_vector(self, from_geopos):
        '''
            computes the unit vector from the given geopos
        '''
        vector = self.pos - from_geopos.get_pos()
        vector /= sqrt(vector.dot(vector))
        # print("unit vector:", vector)
        return vector

    def ENU(self, ref_geopos):
        '''
            Convert from ECEF coordinates to local tangent plane (ENU)
            with origin at ref_geopos
        '''
        lon = ref_geopos.lon
        lat = ref_geopos.lat
        M = np.array([(-sin(lon), -sin(lat) * cos(lon), cos(lat) * cos(lon)),
                      (cos(lon), -sin(lat) * sin(lon), cos(lat) * sin(lon)),
                      (0, cos(lat), sin(lat))])
        M = M.transpose()
        return M.dot(self.pos - ref_geopos.pos)

    def __str__(self):
        s = ''
        if self.name:
            s += self.name + '\n'
        s += "\t {}\n".format(self.pos)
        if self.vel is not None:
            s += "\t {}\n".format(self.vel)
        return s


class Target(GeoPos):
    def __init__(self, t, name, altitude, latitude, longitude,
                 ground_speed=None, azimuth=None):
        # print("ground_speed:", ground_speed, "az:", azimuth)
        GeoPos.__init__(self, latitude, longitude, altitude, name,
                        ground_speed, azimuth)
        self.t0 = t

    def get_time(self):
        return self.t0

    def make_copy(self):
        new_target = Target(self.t0, self.name, 0, 0, 0)
        new_target.pos = self.pos.copy()
        new_target.vel = self.vel.copy()
        return new_target

    def new_pos(self, t):
        # print(t)
        # return self.pos + (t - self.t0) * self.vel
        new_target = self.make_copy()
        new_target.pos = self.pos + (t - self.t0) * self.vel
        return new_target

    def recalc_vel(self, target):
        v = (target.get_pos() - self.get_pos()) / (target.get_time() - self.get_time())
        vabs = sqrt((v**2).sum())
        print("{} new vel: {:.3f} [m/s] ({:.0f} [km/h])".format(
            dt.datetime.isoformat(dt.datetime.utcfromtimestamp(self.get_time())),
            vabs, vabs * 3.6))
        return v

    def vel_recess(self, from_geopos):
        '''
            compute the recession velocity wrt a geopos
        '''
        v = self.unit_vector(from_geopos).dot(self.vel)
        # print("recess vel:", v)
        return v

    def doppler(self, T_geopos, R_geopos):
        '''
            compute the bistatic doppler effect wrt the transmitter and
            receiver geopositions
        '''
        print(self.vel_recess(T_geopos))
        print(self.vel_recess(R_geopos))

        return ((C0 - self.vel_recess(T_geopos)) /
                (C0 + self.vel_recess(R_geopos)))

    def __str__(self):
        s = '{}'.format(self.t0)
        s += GeoPos.__str__(self)
        return s


class PosReport:
    def __init__(self, time, name, alt, lat, lon):
        self.time = time
        self.name = name
        self.alt = alt
        self.lat = lat
        self.lon = lon

    def get_time(self):
        return self.time

    def get_name(self):
        return self.name

    def get_alt(self):
        return self.alt

    def get_lat(self):
        return self.lat

    def get_lon(self):
        return self.lon


class VelReport:
    def __init__(self, time, name, head, vel):
        self.time = time
        self.name = name
        self.head = head
        self.vel = vel

    def get_time(self):
        return self.time

    def get_name(self):
        return self.name

    def get_head(self):
        return self.head

    def get_vel(self):
        return self.vel


# beacon (transmitter)
BEACON = GeoPos(50.097569, 4.588487, 167, 'BEACON')

# receiver location (stations)
stations = [
    # GeoPos(50.935643, 4.369029, 23, 'BEGRIM'),
    # GeoPos(51.145058, 4.464942, 20, 'BEHOVE'),
    # GeoPos(50.950344, 4.594340, 10, 'BEKAMP'),
    # GeoPos(50.667291, 4.579706, 102, 'BEOTTI'),
    # GeoPos(51.204106, 5.432079, 44, 'BEOVER'),
    # GeoPos(49.815163, 5.399523, 403, 'BENEUF'),
    # GeoPos(50.797554, 4.356830, 101, 'BEUCCL'),
    # GeoPos(50.582630, 5.566490, 239, 'BELIEG'),
    # GeoPos(50.008697, 5.218205, 448, 'BETRAN'),
    # GeoPos(50.580139, 5.908796, 336, 'BEJALH'),
    # GeoPos(50.192448, 5.255080, 214, 'BEHUMA'),
    # GeoPos(50.517274, 4.248658, 126, 'BESENE'),
    # GeoPos(50.917834, 2.939487, 14, 'BELANG'),
    # GeoPos(50.856453, 3.329435, 14, 'BEHARE'),
    # GeoPos(50.657077, 4.3482255, 123, 'BEOPHA'),
    # GeoPos(50.957938, 5.536634, 88, 'BEGENK'),
    # GeoPos(50.960007, 4.370530, 30, 'BEHUMB'),
    # GeoPos(50.464331, 3.955228, 33, 'BEMONS'),
    # GeoPos(50.560639, 4.912888, 166, 'BELEUZ'),
    GeoPos(50.247750, 4.925944, 208, 'BEDINA'),
    # GeoPos(51.023194, 3.710111, 8, 'BEGENT'),
    # GeoPos(50.974238, 4.630802, 11, 'BEHAAC'),
    # GeoPos(50.178920, 4.227865, 251, 'BESIVR'),
    # GeoPos(49.683219, 5.520249, 343, 'BETINT'),
    # GeoPos(50.974534, 5.670938, 48, 'BEMAAS'),
    # GeoPos(50.882519, 3.416850, 14, 'BEWARE')
]

if __name__ == "__main__":
    import argparse
    import matplotlib.pyplot as plt

    def GetArguments():
        parser = argparse.ArgumentParser(
            description='''
# Determine the double Doppler shift for a bistatic configuration.
# The principle is tested on aircraft data obtained from ADS-B.
''')
        # parser.add_argument(
        #     "--filename", help="name of aircraft data file", default=None)
        # parser.add_argument(
        #     "--aircraft", help="ID of aircraft", default=None)
        args = parser.parse_args()
        print(args)
        return args

    args = GetArguments()

    '''
       The aircraft data is inserted manually. This should be automated as soon
       as its format has been defined.
    '''

    # aircraft reported positions
    ac_pos_report = [
        PosReport(dt.datetime(2019, 3, 23, 2, 46, 10, 425890,
                              dt.timezone.utc).timestamp(),
                  '505e67', 11277.6, 50.8255, 4.6242),
        PosReport(dt.datetime(2019, 3, 23, 2, 46, 30, 480570,
                              dt.timezone.utc).timestamp(),
                  '505e67', 11277.6, 50.818, 4.6904),
        PosReport(dt.datetime(2019, 3, 23, 2, 46, 40, 704223,
                              dt.timezone.utc).timestamp(),
                  '505e67', 11277.6, 50.8142, 4.7241),
        PosReport(dt.datetime(2019, 3, 23, 2, 47, 36, 605413,
                              dt.timezone.utc).timestamp(),
                  '505e67', 11277.6, 50.793, 4.909)]

    ac_pos_report_2 = [
        PosReport(dt.datetime(2019, 3, 26, 2, 9, 39, 692404,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 11574.78, 50.9834, 4.3043),
        PosReport(dt.datetime(2019, 3, 26, 2, 9, 24, 94558,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 11582.4, 50.9717, 4.3491),
        PosReport(dt.datetime(2019, 3, 26, 2, 9, 8, 957731,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 11582.4, 50.9602, 4.3926),
        PosReport(dt.datetime(2019, 3, 26, 2, 9, 3, 971024,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 11582.4, 50.9564, 4.4069),
        PosReport(dt.datetime(2019, 3, 26, 2, 8, 48, 200829,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 11582.4, 50.9444, 4.4521),
        PosReport(dt.datetime(2019, 3, 26, 2, 8, 36, 384359,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 11582.4, 50.9355, 4.4859),
        PosReport(dt.datetime(2019, 3, 26, 2, 8, 29, 45229,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 11582.4, 50.93, 4.5064),
        PosReport(dt.datetime(2019, 3, 26, 2, 8, 28, 257727,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 11582.4, 50.9293, 4.5092),
        PosReport(dt.datetime(2019, 3, 26, 2, 8, 26, 226749,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 11582.4, 50.9278, 4.5149),
        PosReport(dt.datetime(2019, 3, 26, 2, 8, 11, 351921,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 11582.4, 50.9165, 4.5571),
        PosReport(dt.datetime(2019, 3, 26, 2, 8, 0, 12965,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 11582.4, 50.9079, 4.5895),
        PosReport(dt.datetime(2019, 3, 26, 2, 7, 17, 935614,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 11582.4, 50.876, 4.7089),
        PosReport(dt.datetime(2019, 3, 26, 2, 6, 46, 804770,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 11582.4, 50.8499, 4.8059),
    ]

    # aircraft reported velocities and headings
    ac_vel_report = [
        VelReport(dt.datetime(2019, 3, 23, 2, 45, 28, 287441,
                              dt.timezone.utc).timestamp(),
                  '505e67', 99.8711328196, 853.44 / 3.6),
        VelReport(dt.datetime(2019, 3, 23, 2, 46, 3, 939782,
                              dt.timezone.utc).timestamp(),
                  '505e67', 99.9935802593, 853.76 / 3.6)
    ]

    ac_vel_report_2 = [
        VelReport(dt.datetime(2019, 3, 26, 2, 9, 49, 325921,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 292.650913958, 788.67 / 3.6),
        VelReport(dt.datetime(2019, 3, 26, 2, 9, 27, 630046,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 292.702842123, 786.96 / 3.6),
        VelReport(dt.datetime(2019, 3, 26, 2, 9, 11, 903164,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 292.702842123, 786.96 / 3.6),

        VelReport(dt.datetime(2019, 3, 26, 2, 7, 55, 357259,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 292.807377739, 783.54 / 3.6),
        VelReport(dt.datetime(2019, 3, 26, 2, 7, 53, 848981,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 292.932100438, 784.26 / 3.6),
        VelReport(dt.datetime(2019, 3, 26, 2, 7, 51, 949230, dt.timezone.utc).timestamp(),
                  '46c8c1', 292.932100438, 784.26 / 3.6),
        VelReport(dt.datetime(2019, 3, 26, 2, 7, 46, 510119,
                              dt.timezone.utc).timestamp(),
                  '46c8c1', 292.984934153, 782.56 / 3.6),
    ]

    pac = [Target(p.time, p.name, p.alt, p.lat, p.lon)
           for p in ac_pos_report_2]

    v = np.array([pac[i + 1].recalc_vel(pac[i]) for i in range(len(pac[1:]))])

    ac = pac[len(pac) // 2]
    ac.vel = v.mean(0)

    # aircraft

    t_inter = np.linspace(pac[-1].t0 - 300, pac[0].t0 + 300, 50)
    pac_inter = np.array([ac.new_pos(t) for t in t_inter])
    f0 = 49.970e6
    for station in stations:
        spec = np.array(
            [p.doppler(BEACON, station) for p in pac_inter]) * f0 - f0
        plt.plot(t_inter - pac[0].t0, spec, label=station.name)
    plt.legend()
    plt.title('Aircraft ID:' + pac[0].name)
    plt.xlabel('time [s] w.r.t. {} '.format(
        dt.datetime.isoformat(
            dt.datetime.utcfromtimestamp(pac[0].t0))))
    plt.ylabel('frequency offset [Hz]')
    plt.ylim(-100, 100)
    plt.grid(True)
    plt.show()
