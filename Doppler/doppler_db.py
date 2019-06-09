'''
Created by Justin Botton
16/04/2019
'''

from ORM import ORM
from orm_adsb import orm_adsb
import doppler
import matplotlib.pyplot as plt
from pylab import figure
import numpy as np
import datetime as dt
import sys
import cv2
import brams_wav_spec as wav

database = ORM('adsb-utc')
#database = orm_adsb('adsb')
BEACON = doppler.GeoPos(50.097569, 4.588487, 167, 'BEACON')

if len(sys.argv) == 2 and sys.argv[1]=='help':
    print('To generate a graphic for one receiver with one plane between two dates : \n'
          'python doppler_db.py station_name mode_s start_date end_date \n'
          'Example : python doppler_db.py BEOVER 4ba893 2019-04-15 03:41:18 2019-04-15 03:46:18')

if len(sys.argv) == 6:
    station_name = sys.argv[1]
    start_date = sys.argv[2] + " " + sys.argv[3]
    end_date = sys.argv[4] + " " + sys.argv[5]

    station_data = database.select_station(station_name)
    station = doppler.GeoPos(station_data[0][1], station_data[0][2], station_data[0][3], station_data[0][0])

    output = database.select_aircraft_position_all(start_date, end_date)
    ac_pos_report = [
        doppler.PosReport(dt.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f').timestamp(), row[1], row[2], row[3],
                          row[4])
        for row in output]

    aircraft = {}
    for i in ac_pos_report:
        if i.get_name() not in aircraft:
            aircraft[i.get_name()] = []
        aircraft[i.get_name()].append(doppler.PosReport(i.get_time(), i.get_name(), i.get_alt(), i.get_lat(), i.get_lon()))

    my_file = open('aircraft_data.txt', 'w')

    for i in aircraft:
        pac = [doppler.Target(j.time, j.name, j.alt, j.lat, j.lon) for j in aircraft[i]]

        if len(pac) > 2:
            v = np.array([pac[i + 1].recalc_vel(pac[i]) for i in range(len(pac[1:]))])

            ac = pac[len(pac) // 2]
            ac.vel = v.mean(0)

            # aircraft

            t_inter = np.linspace(pac[0].t0, pac[-1].t0, 4000)  # 1653759
            pac_inter = np.array([ac.new_pos(t) for t in t_inter])
            f0 = 49.970e6
            plt.figure(1, figsize=(11.15, 7.74))
            spec = np.array(
                [p.doppler(BEACON, station) for p in pac_inter]) * f0 - f0
            #plt.plot(t_inter, spec, label=pac[0].get_name())
            my_file.write("Aircraft : "+str(pac[0].get_name())+"\n")

            for y in range(0, len(spec)-1):
                my_file.write(str(spec[y])+", "+str(t_inter[y]-dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').timestamp())+" \n")

            my_file.write('\n')

            spec_wav = wav.BramsSpectrogram(
                'RAD_BEDOUR_20190427_0300_BEUCCL_SYS001.wav', samplerate=None, fcal=1500.0)

            print(len(spec_wav.i_sample))
            # print(np.corrcoef(spec_wav.i_sample, spec))
            plt.plot(spec)
            plt.show()

            plt.plot(t_inter, spec)


            plt.axhline(y=0)
            # plt.axhline(y=1)
            # plt.axvline(x=1)
            plt.title('Aircraft ID:' + pac[0].get_name())
            # plt.legend()

            plt.xlabel(dt.datetime.fromtimestamp(pac[0].get_time()))
            plt.ylabel('frequency offset [Hz]')
            plt.xlim(dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').timestamp(),
                     dt.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').timestamp())
            plt.ylim(-100, 100)
            plt.grid(False)
            plt.savefig('test.png')
            plt.show()
    my_file.close()

if len(sys.argv) == 7 and sys.argv[6] == 'temp_match':
    station_name = sys.argv[1]
    start_date = sys.argv[2] + " " + sys.argv[3]
    end_date = sys.argv[4] + " " + sys.argv[5]

    station_data = database.select_station(station_name)
    station = doppler.GeoPos(station_data[0][1], station_data[0][2], station_data[0][3], station_data[0][0])

    output = database.select_aircraft_position_all(start_date, end_date)
    ac_pos_report = [
        doppler.PosReport(dt.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f').timestamp(), row[1], row[2], row[3],
                          row[4])
        for row in output]

    aircraft = {}
    for i in ac_pos_report:
        if i.get_name() not in aircraft:
            aircraft[i.get_name()] = []
        aircraft[i.get_name()].append(doppler.PosReport(i.get_time(), i.get_name(), i.get_alt(), i.get_lat(), i.get_lon()))

    my_file = open('aircraft_data.txt', 'w')

    for i in aircraft:
        pac = [doppler.Target(j.time, j.name, j.alt, j.lat, j.lon) for j in aircraft[i]]

        if len(pac) > 2:
            v = np.array([pac[i + 1].recalc_vel(pac[i]) for i in range(len(pac[1:]))])

            ac = pac[len(pac) // 2]
            ac.vel = v.mean(0)

            # aircraft

            t_inter = np.linspace(pac[0].t0, pac[-1].t0, 50)
            pac_inter = np.array([ac.new_pos(t) for t in t_inter])
            f0 = 49.970e6
            spec = np.array(
                [p.doppler(BEACON, station) for p in pac_inter]) * f0 - f0

            my_file.write("Aircraft : "+str(pac[0].get_name())+"\n")

            for y in range(0, len(spec)-1):
                my_file.write(str(spec[y])+", "+str(t_inter[y]-dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').timestamp())+" \n")

            my_file.write('\n')

            plt.plot(t_inter, spec)

            plt.axhline(y=0)
            plt.title('Aircraft ID:' + pac[0].get_name())

            plt.xlabel(dt.datetime.fromtimestamp(pac[0].get_time()))
            plt.ylabel('frequency offset [Hz]')
            plt.ylim(spec[-1], spec[0])
            #plt.xlim(dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').timestamp(),
             #        dt.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').timestamp())
            plt.grid(False)
            plt.savefig('test.png')
            plt.show()
    my_file.close()

if len(sys.argv) == 7:
    station_name = sys.argv[1]
    mode_s = sys.argv[2]
    start_date = sys.argv[3]+" "+sys.argv[4]
    end_date = sys.argv[5]+" "+sys.argv[6]

    # Getting Station data
    station_data = database.select_station(station_name)
    station = doppler.GeoPos(station_data[0][1], station_data[0][2], station_data[0][3], station_data[0][0])

    # Getting Position data
    output = database.select_aircraft_position(mode_s, start_date, end_date)
    ac_pos_report = [doppler.PosReport(dt.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f').timestamp(), row[1], row[2], row[3], row[4])
                     for row in output]

    # Getting Speed and Heading data
    output = database.select_aircraft_speed_heading(mode_s, start_date, end_date)
    ac_vel_report = [doppler.VelReport(dt.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f').timestamp(), row[1], row[2], (row[3]/3.6))
                     for row in output]

    pac = [doppler.Target(p.get_time(), p.get_name(), p.get_alt(), p.get_lat(), p.get_lon())
           for p in ac_pos_report]

    v = np.array([pac[i + 1].recalc_vel(pac[i]) for i in range(len(pac[1:]))])

    ac = pac[len(pac) // 2]
    ac.vel = v.mean(0)

    # aircraft

    #t_inter = np.linspace(dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').timestamp() - 150, dt.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').timestamp() + 150, 50)
    t_inter = np.linspace(pac[0].t0, pac[-1].t0, 50)

    pac_inter = np.array([ac.new_pos(t) for t in t_inter])
    f0 = 49.970e6
    spec = np.array(
        [p.doppler(BEACON, station) for p in pac_inter]) * f0 - f0
    #plt.plot(t_inter, spec, label=station.get_name())
    plt.legend()
    plt.title('Aircraft ID:' + pac[0].get_name())
    plt.xlabel(dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S'))
    plt.ylabel('frequency offset [Hz]')
    plt.ylim(-100, 100)
    plt.xlim(dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').timestamp(), dt.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').timestamp())
    plt.grid(False)
    plt.figure(figsize=(7, 4))
    plt.show()

# EOF
