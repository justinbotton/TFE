# Justin Botton EPHEC 2019

# get Aircraft ID
# @param : adsb frame
# @return : aircraft id
def ident(frame):
    ident = str(frame[2:8])
    return ident
# end id


# EOF
