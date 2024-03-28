import xpc

# 创建 XPlaneConnect 对象
client = xpc.XPlaneConnect()

# 为要监视的变量创建订阅列表
datarefs = [
    "sim/flightmodel/position/local_x",
    "sim/flightmodel/position/local_y",
    "sim/flightmodel/position/local_z",
    "sim/flightmodel/position/theta",
    "sim/flightmodel/position/phi",
    "sim/flightmodel/position/psi",
    "sim/cockpit2/gauges/indicators/altitude_ft_pilot",
]

lat_rwy_id = [34.134, -118.322]  # 参数包括纬度、经度以及跑道编号
rwy_info = client.getAPTInfo(lat_rwy_id)
if rwy_info is None:
    print("获取跑道信息失败！")
else:
    print(f"当前机场：{rwy_info['name']}")
    for rwy in rwy_info["runways"]:
        if rwy["ident"] == lat_rwy_id[2]:
            rwy_elev = rwy["elevation_m"]
            rwy_lat = rwy["latitude_deg"]
            rwy_lon = rwy["longitude_deg"]
            break

# 启动数据监听器，并设置初始的本地位置和朝向
monitor_vars = client.subscribeData(datarefs, [])
posi = client.getPOSI()
attitude = client.getCTRL()
local_x, local_y, local_z = posi["local_x"], posi["local_y"], posi["local_z"]
theta, phi, psi = attitude["pitch"], attitude["roll"], attitude["heading"]

while True:
    # 不断地获取姿态和位置信息，计算水平距离和高度与跑道的差值
    posi = client.getPOSI()
    local_x, local_y, local_z = posi["local_x"], posi["local_y"], posi["local_z"]
    altitude_ft = client.getDREF("sim/cockpit2/gauges/indicators/altitude_ft_pilot")[0]
    altitude_m = altitude_ft * 0.3048  # 转换为米
    rwy_altitude_m = rwy_elev + altitude_m  # 飞机当前高度与跑道高度之和
    dist_horizontal_m = ((local_x - rwy_lat) ** 2 + (local_y - rwy_lon) ** 2) ** 0.5  # 计算水平距离

    # 输出结果
    print(f"跑道 {lat_rwy_id[2]} 和飞机的高度差：{rwy_altitude_m - local_z} 米")
    print(f"跑道 {lat_rwy_id[2]} 和飞机的水平距离：{dist_horizontal_m} 米")

    # 等待一段时间再重复操作
    client.pauseSim(False)
    client.sendCOMM("sim/operation/quit")  # Ctrl-C 终止程序时，自动退出 X-Plane 的飞行模式
    client.pauseSim(True)