import pyrealsense2 as rs

# カメラパイプラインを作成
pipe = rs.pipeline()

# ストリームの設定
conf = rs.config()

# 使用可能なデバイスプロファイルをリスト化
pipeline_wrapper = rs.pipeline_wrapper(pipe)
pipeline_profile = conf.resolve(pipeline_wrapper)

device = pipeline_profile.get_device()
sensor = device.query_sensors()[0]

print("Supported resolutions and formats:")
for profile in sensor.get_stream_profiles():
    print(profile)
