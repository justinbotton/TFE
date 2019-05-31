# Justin Botton EPHEC 2019


# main call
# @param : adsb frame
# @return : Aircraft name
def name(frame):
    frame = frame[10:22]
    return nameCalc(frame)
# end name


# dictionnary for decoding Aircraft Name
# @param : decimal number
# @return : char corresponding to the given number
def dec2char(decNumber):
    index = '#ABCDEFGHIJKLMNOPQRSTUVWXYZ#####_###############0123456789######'
    return index[decNumber]
# end dec2char


# decode Aircraft Name
# @param : adsb frame
# @return : Aircraft name
def nameCalc(frame):
    output = ""
    binary = "{0:048b}".format(int(frame, 16)) # parsing the hexa frame to binary
    for i in range (0, 48, 6):
        dec = int(binary[i:i + 6], 2)
        output += dec2char(dec)
    return output
# end nameCalc
