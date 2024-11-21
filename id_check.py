import pyrealsense2 as rs

# カメラの情報を取得
ctx = rs.context()
devices = ctx.query_devices()

# 接続されているカメラのIDを表示
for i, device in enumerate(devices):
    print(f"Camera {i}: {device.get_info(rs.camera_info.name)}")


import pyrealsense2 as rs

# コンテキストを作成して、接続されているデバイスの情報を取得
context = rs.context()

# 接続されているすべてのデバイスをリストアップ
for device in context.devices:
    print(f"Device: {device.get_info(rs.camera_info.name)}")
    print(f"Serial Number: {device.get_info(rs.camera_info.serial_number)}")
