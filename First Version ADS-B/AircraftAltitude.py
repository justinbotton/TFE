# Justin Botton EPHEC 2019


# main call
# @param : adsb frame
# @return : Aircraft altitude
def altitude(frame):
    alt, mult = hex2dec(frame[10:13])
    return altitudeCalc(alt, mult)
# end altitude


# decode Aircraft altitude
# @param : adsb  frame
# @return : altitude in decimal from frame
def hex2dec(frame):
    multiple = 0
    binary = "{0:4b}".format(int(frame, 16))
    if binary[7] == "1":
        multiple = 25
    elif binary[7] == "0":
        multiple = 25
    binary = binary[:7] + binary[(7 + 1):]
    output = int(binary, 2)
    return output, multiple
# end hex2dec


# calculate the altitude in meters
# @param decNumber : altitude in decimal
# @param multiple : multiple of the altitude
# @return : altitude in meters
def altitudeCalc(decNumber, multiple):
    altitudeFT = (decNumber * multiple) - 1000
    altitudeMeters = altitudeFT * 0.3048
    return altitudeMeters
# end altitudeMeters


# EOF
