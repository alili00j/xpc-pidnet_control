import sys

import xpc
from datetime import datetime, timedelta
import PID
import time
import math, numpy

update_interval = 0.125 #seconds
start = datetime.now()
last_update = start

P = 0.05
I = 0.01
D = 0

desired_roll = 0 # init at flat and level - will be overridden by heading control
desired_pitch = 2 # init at flat and level - will be overridden by altitude control
desired_speed = 160
desired_alt = 8000.0
desired_hdg = 140

roll_PID = PID.PID(P*2, I*2, D)
roll_PID.SetPoint = desired_roll

pitch_PID = PID.PID(P, I, D)
pitch_PID.SetPoint = desired_pitch

altitude_PID = PID.PID(P*2, I*2, D)
altitude_PID.SetPoint = desired_alt

speed_PID = PID.PID(P, I, D)
speed_PID.SetPoint = desired_speed

heading_error_PID = PID.PID(1,0.05,0.1)
heading_error_PID.SetPoint = 0 # need heading error to be 0

DREFs = ["sim/cockpit2/gauges/indicators/airspeed_kts_pilot",
        "sim/cockpit2/gauges/indicators/heading_electric_deg_mag_pilot",
        "sim/flightmodel/failures/onground_any",
        "sim/flightmodel/misc/h_ind"]

def normalize(value, min=-1, max=1):
    if (value > max):
        return max
    elif (value == 180.0):
        r -= 360.0
        return r
    elif (value < min):
        return min
    else:
        return value
    
def get_angle_difference(desired_hdg, current_hdg):
    angle_difference = desired_hdg - current_hdg
    return angle_difference


# https://gist.github.com/jeromer/2005586
def calculate_initial_compass_bearing(pointA, pointB):
    """
    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

# https://janakiev.com/blog/gps-points-distance-python/
def haversine(coord1, coord2):
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2) 
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))

KBJC_lat = 39.9088056
KBJC_lon = -105.1171944

def monitor():
    global last_update
    with xpc.XPlaneConnect() as client:
        while True:
            if (datetime.now() > last_update + timedelta(milliseconds=update_interval*1000)):
                last_update = datetime.now()
                print(f"loop start - {datetime.now()}")
                posi = client.getPOSI()
                ctrl = client.getCTRL()

                bearing_to_kbjc = calculate_initial_compass_bearing((posi[0], posi[1]), (KBJC_lat, KBJC_lon))
                dist_to_kbjc = haversine((posi[0], posi[1]), (KBJC_lat, KBJC_lon))
                #desired_hdg = 116 #bearing_to_kbjc

                multi_DREFs = client.getDREFs(DREFs) #speed=0, mag hdg=1, onground=2

                #https://github.com/nasa/XPlaneConnect/wiki/getDREF
                #speed_DREF = client.getDREF()

                current_roll = posi[4]
                current_pitch = posi[3]
                #current_hdg = posi[5] # this is true, need to use DREF to get mag ''
                current_hdg = multi_DREFs[1][0]
                current_altitude = multi_DREFs[3][0]
                current_asi = multi_DREFs[0][0]
                onground = multi_DREFs[2][0]
                heading_error = get_angle_difference(desired_hdg, current_hdg)

                # outer loops first
                altitude_PID.update(current_altitude)
                heading_error_PID.update(heading_error)

                # heading_PID, not yet implemented

                new_pitch_from_altitude = normalize(altitude_PID.output, -10, 10)
                new_roll_from_heading_error = normalize(heading_error_PID.output, -25, 25)
                # if new_pitch_from_altitude > 15:
                # new_pitch_from_altitude = 15
                # elif new_pitch_from_altitude < -15:
                # new_pitch_from_altitude = -15

                pitch_PID.SetPoint = new_pitch_from_altitude
                roll_PID.SetPoint = new_roll_from_heading_error

                roll_PID.update(current_roll)
                speed_PID.update(current_asi)
                pitch_PID.update(current_pitch)

                new_ail_ctrl = normalize(roll_PID.output, min=-1, max=1)
                new_ele_ctrl = normalize(pitch_PID.output, min=-1, max=1)
                new_thr_ctrl = normalize(speed_PID.output, min=0, max=1)

                if (onground != 1.0):
                    ctrl = [new_ele_ctrl, new_ail_ctrl, 0.0, new_thr_ctrl] # ele, ail, rud, thr. -998 means don't change
                    client.sendCTRL(ctrl)
                else:
                    print("on ground, not sending controls")

                output = f"current values -- roll: {current_roll: 0.3f}, pitch: {current_pitch: 0.3f}, hdg: {current_hdg:0.3f}, alt: {current_altitude:0.3f}, asi: {current_asi:0.3f}"
                output = output + "\n" + f"hdg error: {heading_error: 0.3f}"
                output = output + "\n" + f"new ctrl positions -- ail: {new_ail_ctrl: 0.4f}, ele: {new_ele_ctrl: 0.4f}, thr: {new_thr_ctrl:0.4f}"
                output = output + "\n" + f"PID outputs -- altitude: {altitude_PID.output: 0.4f}, pitch: {pitch_PID.output: 0.4f}, ail: {roll_PID.output: 0.3f}, hdg: {heading_error_PID.output: 0.3f}"
                output = output + "\n" + f"bearing to KBJC: {bearing_to_kbjc:3.1f}, dist: {dist_to_kbjc*0.000539957:0.2f} NM"
                output = output + "\n" + f"loop end - {datetime.now()}"
                output = output + "\n"
                print(output)
                time.sleep(0.005)

if __name__ == "__main__":
    monitor()