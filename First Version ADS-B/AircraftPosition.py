# Justin Botton EPHEC 2019

import math


# main call for latitude
# @param frameEven : adsb even frame
# @param frameOdd : adsb odd frame
# @return latitude
def latitude(frameEven, frameOdd):
    even, t0 = hex2dec(frameEven[13:22], "lat")
    odd, t1 = hex2dec(frameOdd[13:22], "lat")
    even = even / 131072.0
    odd = odd / 131072.0
    return latitudeCalc(even, odd, t0, t1)
# end latitude


def unaLatitude(prevLat, frame, parity):
    latCpr, t = hex2dec(frame[13:22], "lat")
    latCpr = latCpr / 131072.0
    dLat = 0
    if parity == "0":
        dLat = 360.0 / 60.0
    elif parity == "1":
        dLat = 360.0 / 59.0
    j = math.floor(prevLat / dLat) + math.floor((math.fmod(prevLat, dLat) / dLat) - latCpr + 0.5)
    latitude = dLat * (j + latCpr)
    return round(latitude, 4)



# main call or longitude
# @param frameEven : adsb even frame
# @param frameOdd : adsb odd frame
# @param latitude : latitude previously calculated
# @return : Aircraft longitude
def longitude(frameEven, frameOdd, latitude):
    even, t0 = hex2dec(frameEven[13:22], "long")
    odd, t1 = hex2dec(frameOdd[13:22], "long")
    even = even / 131072.0
    odd = odd / 131072.0
    return longitudeCalc(even, odd, latitude, t0, t1)
# en longitude



def unaLongitude(prevLon, frame, parity, lat):
    dLon = 0
    lonCpr, t = hex2dec(frame[13:22], "long")
    lonCpr = lonCpr / 131072.0
    nlLat = cprNL(lat)
    if parity == "0":
        if nlLat > 0:
            dLon = 360.0 / nlLat
        elif nlLat == 0:
            dLon = 360.0
    elif parity == "1":
        if nlLat - 1 > 0:
            dLon = 360.0 / (nlLat - 1)
        elif nlLat - 1 == 0:
            dLon = 360.0
    m = math.floor(prevLon / dLon) + math.floor((math.fmod(prevLon, dLon) / dLon) - lonCpr + 0.5)
    longitude = dLon * (m + lonCpr)
    return round(longitude, 4)

# parsing hexa frame to get 17 bin numbers and parsing them to get the value
# @param frame : adsb frame
# @param coord : if its latitude or longitude
# @return : latitude / longitude decimal value
def hex2dec(frame, coord):
    binary = "{0:036b}".format(int(frame, 16))
    t = binary[0]
    if coord == "lat":
        binary = binary[2:19]
    elif coord == "long":
        binary = binary[19:36]
    output = int(binary, 2)
    return output, t
# end hex2dec


# calculate the latitude
# @param latEven_cpr : decimal latitude value from even frame
# @param latOdd_cpr : decimal latitude vlaue from odd frame
# @param t0 : time even frame
# @param t1 : time odd frame
# @return latitude : Aircraft latitude
def latitudeCalc(latEven_cpr, latOdd_cpr, t0, t1):
    j = math.floor((59 * latEven_cpr) - (60 * latOdd_cpr) + 0.5)
    latitudeEven = (360.0 / 60) * (math.fmod(j, 60) + latEven_cpr)
    latitudeOdd = (360.0 / 59) * (math.fmod(j, 59) + latOdd_cpr)
    if latitudeEven >= 270:
        latitudeEven = latitudeEven - 360
    if latitudeOdd >= 270:
        latitudeOdd = latitudeOdd - 360
    if cprNL(latitudeEven) != cprNL(latitudeOdd):
        return "Inconsistent LAT"
    if t0 >= t1:
        return round(latitudeEven, 4)
    return round(latitudeOdd, 4)
# end latitudeCalc


# calculate the longitude
# @param lonEven_cpr : decimal longitude value from even frame
# @param lonOdd_cpr : decimal longitude value from odd frame
# @param lat : latitude previously calculated
# @param t0 : time even frame
# @param t1 : time odd frame
def longitudeCalc(lonEven_cpr, lonOdd_cpr, lat, t0, t1):
    j = math.floor(lonEven_cpr * (cprNL(lat) - 1) - lonOdd_cpr * cprNL(lat) + 0.5)
    if t0 >= t1:
        ni = cprN(lat, 0)
        lon = (360.0 / ni) * (math.fmod(j, ni) + lonEven_cpr)
    else:
        ni = cprN(lat, 1)
        lon = (360.0 / ni) * (math.fmod(j, ni) + lonOdd_cpr)
    if lon > 180:
        lon = lon - 180
    return round(lon, 4)
# end longitudeCalc


def cprN(lat, isOdd):
    nl = cprNL(lat) - isOdd
    if nl > 1:
        return nl
    return 1
# en cprN


def cprNL(lat):
    try:
        nz = 15
        a = 1 - math.cos(math.pi / (2 * nz))
        b = math.cos(math.pi / 180.0 * abs(lat)) ** 2
        nl = 2 * math.pi / (math.acos(1 - a/b))
        NL = math.floor(nl)
        return NL
    except:
        return 1
# en cprNL
