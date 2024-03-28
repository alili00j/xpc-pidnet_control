import sys
import xpc
import PID
import math
import time
from socket import *
from datetime import datetime, timedelta
from geopy.distance import geodesic

update_interval = 0.05 # seconds
start = datetime.now()
last_update = start

# defining the initial PID values
P = 0.1 # PID library default = 0.2
I = P/10 # default = 0
D = 0 # default = 0
#跑道经纬度
final_lat = 31.126039178
final_lon = 121.79423244
# initializing both PID controllers(
roll_PID = PID.PID(P, I, D)
pitch_PID = PID.PID(P, I, D)
yaw_PID = PID.PID(P, I, D)

mid_alt = 200
final_pitch = 4
#拉机头的高度和跑道高度
final_alt = 26
last_alt = 6.85
# setting the desired values
# roll = 0 means wings level
# pitch = 2 means slightly nose up, which is required for level flight

# 设置需要读取的数据引用
DATA_REF_FLAPS_DEG = "sim/cockpit2/controls/flap_ratio"
DATA_REF_THROTTLE = "sim/cockpit2/engine/actuators/throttle_ratio_all"
DATA_REF_VELOCITY_KTS = "sim/flightmodel/position/indicated_airspeed"

# def init_socket():
#     # 创建套接字
#     tcp_server = socket(AF_INET, SOCK_STREAM)
#     address = ('', 8000)
#     tcp_server.bind(address)
#     tcp_server.listen(128)
#     client_socket, clientAddr = tcp_server.accept()
#     return  client_socket, clientAddr
#
# def get_data(client_socket):
#     from_client_msg = client_socket.recv(1024)  # 接收1024给字节,这里recv接收的不再是元组，区别UDP
#     error_data = int.from_bytes(from_client_msg, 'big')
#     return error_data

def monitor():
    global last_update
    with xpc.XPlaneConnect() as client:
        # client_socket, _ = init_socket()
        while client is not None:
            if (datetime.now() > last_update + timedelta(milliseconds = update_interval * 1000)):

                # error_data = get_data(client_socket)
                # print('当前偏差:{}'.format(error_data))
                last_update = datetime.now()
                print(f"loop start - {datetime.now()}")

                posi = client.getPOSI();
                ctrl = client.getCTRL();
                #放下起落架
                client.sendDREF("sim/cockpit2/controls/gear_handle_down",1)
                # 读取空速的值
                velocity_kts = client.getDREF(DATA_REF_VELOCITY_KTS)[0]

                print("当前空速为：", velocity_kts, "knots")

                # 读取油门的值
                # throttle_ratio = client.getDREF(DATA_REF_THROTTLE)[0]
                # print("当前油门的值为：", throttle_ratio)
                gear = posi[6]
                print("当前起落架状态为：", gear)



                # 读取襟翼角度的值
                flaps_deg = client.getDREF(DATA_REF_FLAPS_DEG)[0]

                print("当前襟翼的角度值为：", flaps_deg)
                #
                # print(client.getDREF("sim/flightmodel/version"))

                current_lat = posi[0]
                current_lon = posi[1]
                current_alt = posi[2]
                current_roll = posi[4]
                current_pitch = posi[3]
                current_yaw = posi[5]

                dist = geodesic((current_lat, current_lon), (final_lat, final_lon)).m
                print("当前距离为：", dist)
                print("当前经度为：", current_lat)
                print("当前纬度为：", current_lon)
                print("当前高度为：", current_alt)

                #在拉起机头之前的纵横向操控
                if current_alt > final_alt:
                    # desired_roll = 0
                    # desired_pitch = 1.21
                    # desired_yaw = 342.00
                    # target_roll = -15.0
                    #
                    # if error_data > 0:
                    #     roll_PID.SetPoint = 15.0
                    #     pitch_PID.SetPoint = desired_pitch
                    #     yaw_PID.SetPoint = desired_yaw
                    #     roll_PID.update(current_roll)
                    #     pitch_PID.update(current_pitch)
                    #     yaw_PID.update(current_yaw)
                    #     # time.sleep(1)
                    # elif error_data < 0:
                    #     roll_PID.SetPoint = -15.0
                    #     pitch_PID.SetPoint = desired_pitch
                    #     yaw_PID.SetPoint = desired_yaw
                    #     roll_PID.update(current_roll)
                    #     pitch_PID.update(current_pitch)
                    #     yaw_PID.update(current_yaw)
                    #     # time.sleep(1)
                    # else:
                    #     roll_PID.SetPoint = desired_roll
                    #     pitch_PID.SetPoint = desired_pitch
                    #     yaw_PID.SetPoint = desired_yaw
                    #     roll_PID.update(current_roll)
                    #     pitch_PID.update(current_pitch)
                    #     yaw_PID.update(current_yaw)

                    desired_roll = 0
                    desired_pitch = 1.21
                    desired_yaw = 342.00
                    # target_roll = -15.0
                    # if current_alt > mid_alt and current_alt < 220:
                    #     roll_PID.SetPoint = target_roll
                    #     pitch_PID.SetPoint = desired_pitch
                    #     yaw_PID.SetPoint = desired_yaw
                    #     roll_PID.update(current_roll)
                    #     pitch_PID.update(current_pitch)
                    #     yaw_PID.update(current_yaw)
                    #     time.sleep(0.05)
                    # if current_alt > 250 and current_alt < 270:
                    #     roll_PID.SetPoint = target_roll
                    #     pitch_PID.SetPoint = desired_pitch
                    #     yaw_PID.SetPoint = desired_yaw
                    #     roll_PID.update(current_roll)
                    #     pitch_PID.update(current_pitch)
                    #     yaw_PID.update(current_yaw)
                    #     time.sleep(0.05)
                    # else:
                    # # setting the PID set points with our desired values
                    roll_PID.SetPoint = desired_roll
                    pitch_PID.SetPoint = desired_pitch
                    yaw_PID.SetPoint = desired_yaw
                    roll_PID.update(current_roll)
                    pitch_PID.update(current_pitch)
                    yaw_PID.update(current_yaw)

                #主轮离跑道20英尺拉起机头
                if current_alt > last_alt and current_alt<final_alt:
                    desired_roll = 0
                    desired_pitch = 3
                    desired_yaw = 342.00
                    roll_PID.SetPoint = desired_roll
                    pitch_PID.SetPoint = desired_pitch
                    yaw_PID.SetPoint = desired_yaw
                    roll_PID.update(current_roll)
                    pitch_PID.update(current_pitch)
                    yaw_PID.update(current_yaw)
                #落地踩刹车，拉反推至80空速
                else:
                    desired_roll = 0
                    desired_pitch = 1.5
                    desired_yaw = 341.80
                    roll_PID.SetPoint = desired_roll
                    pitch_PID.SetPoint = desired_pitch
                    yaw_PID.SetPoint = desired_yaw
                    roll_PID.update(current_roll)
                    pitch_PID.update(current_pitch)
                    yaw_PID.update(current_yaw)
                    client.sendDREF("sim/cockpit2/controls/left_brake_ratio", 1)
                    client.sendDREF("sim/cockpit2/controls/right_brake_ratio", 1)
                    if velocity_kts > 80 :
                        client.sendDREF("sim/flightmodel2/engines/thrust_reverser_deploy_ratio", 1)
                    else:
                        client.sendDREF("sim/flightmodel2/engines/thrust_reverser_deploy_ratio", 0)

                new_ail_ctrl = roll_PID.output
                new_ele_ctrl = pitch_PID.output
                new_rud_ctrl = yaw_PID.output

                ctrl = [new_ele_ctrl, new_ail_ctrl, new_rud_ctrl , -998] # ele, ail, rud, thr. -998 means don't change
                client.sendCTRL(ctrl)

                output = f"current values --    roll: {current_roll: 0.3f},  pitch: {current_pitch: 0.3f},  yaw: {current_yaw: 0.3f}"
                output = output + "\n" + f"PID outputs    --    roll: {roll_PID.output: 0.3f},  pitch: {pitch_PID.output: 0.3f},   yaw: {yaw_PID.output: 0.3f}"
                output = output + "\n"
                print(output)

if __name__ == "__main__":

    monitor()