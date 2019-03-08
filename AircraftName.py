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
    switcher = {
            1: "A",
            2: "B",
            3: "C",
            4: "D",
            5: "E",
            6: "F",
            7: "G",
            8: "H",
            9: "I",
            10: "J",
            11: "K",
            12: "L",
            13: "M",
            14: "N",
            15: "O",
            16: "P",
            17: "Q",
            18: "R",
            19: "S",
            20: "T",
            21: "U",
            22: "V",
            23: "W",
            24: "X",
            25: "Y",
            26: "Z",
            48: "0",
            49: "1",
            50: "2",
            51: "3",
            52: "4",
            53: "5",
            54: "6",
            55: "7",
            56: "8",
            57: "9",
            32: "_"
    }
    return switcher.get(decNumber, "?")
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
