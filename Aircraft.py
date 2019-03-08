#Justin Botton EPHEC 2019

import sys
import threading
import Queue
import datetime
from AircraftThread import Affiche
from AircraftId import ident
from AircraftName import name
from AircraftSpeed import speed
from AircraftAltitude import altitude
from AircraftPosition import longitude, latitude, unaLatitude, unaLongitude


# decode the type code
# @param : adsb frame
# @return : type code
def typeCode(frame):
    tcHex = frame[8:10]
    tc = int(hex2bin(tcHex), 2)
    return tc
# end typeCode


# parse the hexa into binary
# @param : frame
# @return : frame parsed in binary
def hex2bin(frame):
    binary = "{0:08b}".format(int(frame, 16))
    output = binary[0:5]
    return output
# end hex2bin


# checking frame integrity
# @param : adsb frame
# @return : if frame is corrupted or not
def integrity(frame):
    gen = list("1111111111111010000001001")
    framebin = list("{0:048b}".format(int(frame, 16)))
    for i in range(len(framebin) - 24):
        if framebin[i] == "1":
            for j in range(len(gen)):
                framebin[i+j] = str((int(framebin[i+j]) ^ int(gen[j])))
            # end for
        # end if
    # end for
    checksum = ''.join(framebin[-24:])
    isConsistent = True
    if checksum != "000000000000000000000000":
        isConsistent = False
        #sys.stdout.write(" CONSISTENT ")
    return isConsistent
# end integrity


# Filling dictionary of Aircrafts
# @param dictionary : Aircraft dictionnary
# @param ident : Aircraft id
# @param frame : adsb framedi
def aircraftDict(dictionary, ident, frame):
    lat = 0
    lon = 0
    parity = "{0:048b}".format(int(frame, 16))[53]
    if ident not in dictionary:
        dictionary[ident] = {}
    if parity == "0":
        dictionary[ident][0] = frame
        dictionary[ident]['evenTime'] = datetime.datetime.now()
        sys.stdout.write(" EVEN ")
        sys.stdout.flush()
    elif parity == "1":
        dictionary[ident][1] = frame
        dictionary[ident]['oddTime'] = datetime.datetime.now()
        sys.stdout.write(" ODD ")
        sys.stdout.flush()
    if dictionary[ident].has_key(0) and dictionary[ident].has_key(1) and not dictionary[ident].has_key('lat'):
        evenTime = dictionary[ident]['evenTime']
        oddTime = dictionary[ident]['oddTime']
        diffTime = 0
        if evenTime > oddTime:
            diffTime = (evenTime - oddTime).total_seconds()
        else:
            diffTime = (oddTime - evenTime).total_seconds()
        if diffTime < 55:
            print(diffTime)
            even = dictionary[ident][0]
            odd = dictionary[ident][1]
            lat = latitude(even, odd)
            lon = longitude(even, odd, lat)
            dictionary[ident]['lat'] = lat
            dictionary[ident]['lon'] = lon
    elif dictionary[ident].has_key('lat') and dictionary[ident].has_key('lon'):
        frame = ""
        if parity == "0":
            frame = dictionary[ident][0]
        elif parity == "1":
            frame = dictionary[ident][1]
        lat = unaLatitude(dictionary[ident]['lat'], frame, parity)
        lon = unaLongitude(dictionary[ident]['lon'], frame, parity, lat)
        dictionary[ident]['lat'] = lat
        dictionary[ident]['lon'] = lon
    return lat, lon
# end aircraftDict


dictionary = {}
q = Queue.Queue()

while True:
    line = sys.stdin.readline()
    if line.startswith("*8d"):
        q.put(line)
        frame = q.get(q.qsize())[1:29]
        isConsistent = integrity(frame)
        if isConsistent:
            tc = typeCode(frame)
            identifiant = ident(frame)
            sys.stdout.write(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " : " + identifiant + " " + str(tc) + " ")
            sys.stdout.flush()
            if tc == 19:
                aircraftSpeed, heading, vertDir, vertRate, vertSrc = speed(frame)
                sys.stdout.write(str(aircraftSpeed) + " km/h ")
                sys.stdout.write(str(heading) + " deg ")
                sys.stdout.write(str(vertDir) + "\n") #" " + str(vertRate) + " fpm (" + vertSrc + ") \n")
                sys.stdout.flush()
            elif 9 <= tc <= 18:
                alt = altitude(frame)
                lat, lon = aircraftDict(dictionary, identifiant, frame)
                sys.stdout.write(str(alt) + " meters lat : " + str(lat) + " long : " + str(lon))
                sys.stdout.flush()
            elif 1 <= tc <= 4:
                aircraftName = name(frame)
                sys.stdout.write(aircraftName + "\n")
                sys.stdout.flush()
            sys.stdout.write("\n")

        #condition.acquire()
        #condition.notify()
# EOF
