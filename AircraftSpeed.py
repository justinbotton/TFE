# Justin Botton EPHEC 2019

import math


# get all speed and heading infos
# @param : adsb frame
# @return : speed and heading infos
def speed(frame):
    frame = frame[8:22]
    S_ew, V_ew, S_ns, V_ns, VrSrc, S_vr, Vr = hex2dec(frame)
    speed, direction = speedCalc(S_ew, V_ew, S_ns, V_ns)
    vertDir, vertRate, vertSrc = verticalrate(VrSrc, S_vr, Vr)
    return speed, direction, vertDir, vertRate, vertSrc
# end speed


# parse frame in decimals values
# @param : adsb frame
# @return : decimals values
def hex2dec(frame):
    binary = "{0:048b}".format(int(frame, 16))
    S_ew = int(binary[13], 2)
    V_ew = int(binary[14:24], 2)
    S_ns = int(binary[24], 2)
    V_ns = int(binary[25:35], 2)
    VrSrc = binary[35]
    S_vr = binary[36]
    Vr = int(binary[37:46], 2)
    return S_ew, V_ew, S_ns, V_ns, VrSrc, S_vr, Vr
# end hex2dec


# calculate Aircraft speed and heading
# @param S_ew : EastWest velocity sign
# @param V_ew : EastWest velocity
# @param S_ns : NorthSouth velocity sign
# @param V_ns : NorthSouth velocity
# @return : speed and heading
def speedCalc(S_ew, V_ew, S_ns, V_ns):
    vwe = 0
    vsn = 0
    if S_ew == 0:
        vwe = V_ew - 1
    elif S_ew == 1:
        vwe = -1 * (V_ew -1)
    if S_ns == 0:
        vsn = V_ns - 1
    elif S_ns == 1:
        vsn = -1 * (V_ns - 1)
    direction = heading(vwe, vsn)
    vwe = math.pow(vwe, 2)
    vsn = math.pow(vsn, 2)
    speedKT = math.sqrt(vwe + vsn)
    speedKMH = speedKT * 1.852
    return round(speedKMH, 2), direction
# end speedCalc


# decode Aircraft heading
# @param Vwe : WestEast velocity
# @param Vsn : SouthNorth velocity
# @return : Aircraft heading
def heading(Vwe, Vsn):
    heading = math.atan2(Vwe, Vsn) * (360.0 / (2 * math.pi))
    if heading < 0:
        heading = heading + 360.0
    return heading
# end heading


# give the point of compass according to the heading
# @param : heading in degrees
# @return : point of compass according to Aircraft heading
def direction(heading):
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
        return "SSO"
    elif 213.76 <= heading <= 236.25:
        return "SO"
    elif 236.26 <= heading <= 258.75:
        return "OSO"
    elif 258.76 <= heading <= 281.25:
        return "O"
    elif 281.26 <= heading <= 303.75:
        return "ONO"
    elif 303.76 <= heading <= 326.25:
        return "NO"
    elif 326.26 <= heading <= 337.25:
        return "NNO"
    elif 337.26 <= heading <= 360:
        return "N"
# end direction


# decode vertical rate infos
# @param VrSrc : vertical rate source
# @param S_vr : vertical rate sign
# @param Vr : vertical rate
# @return : vertical rate infos
def verticalrate(VrSrc, S_vr, Vr):
    directionVerticalMvmt = ""
    verticalRateSrc = ""
    if S_vr == "1":
        directionVerticalMvmt = "DOWN"
    elif S_vr == "0":
        directionVerticalMvmt = "UP"
    verticalRate = (Vr - 1) * 64
    if VrSrc == "1":
        verticalRateSrc = "Geometric altitude change rate"
    elif VrSrc == "0":
        verticalRateSrc = "Baro-pressure altitude change rate"
    return directionVerticalMvmt, verticalRate, verticalRateSrc
# end verticalrate


# EOF

