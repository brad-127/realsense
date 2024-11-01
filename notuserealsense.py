import pyrealsense2 as rs
import numpy as np
import cv2

# カメラの設定
conf = rs.config()

# RGBストリーム
conf.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
# 距離ストリーム
conf.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

# stream開始
pipe = rs.pipeline()
profile = pipe.start(conf)

# フィルターの設定
decimate = rs.decimation_filter()
decimate.set_option(rs.option.filter_magnitude, 1)

spatial = rs.spatial_filter()
spatial.set_option(rs.option.filter_magnitude, 1)
spatial.set_option(rs.option.filter_smooth_alpha, 0.25)
spatial.set_option(rs.option.filter_smooth_delta, 50)

hole_filling = rs.hole_filling_filter()

depth_to_disparity = rs.disparity_transform(True)
disparity_to_depth = rs.disparity_transform(False)

# alignモジュールの定義
align_to = rs.stream.color
align = rs.align(align_to)

try:
    while True:
        frames = pipe.wait_for_frames()
        
        # frameデータを取得
        aligned_frames = align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        if not color_frame or not depth_frame:
            continue

        # 画像データに変換
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        # 距離データのフィルター処理
        filter_frame = decimate.process(depth_frame)
        filter_frame = depth_to_disparity.process(filter_frame)
        filter_frame = spatial.process(filter_frame)
        filter_frame = disparity_to_depth.process(filter_frame)
        filter_frame = hole_filling.process(filter_frame)
        result_frame = filter_frame.as_depth_frame()

        # 距離情報の取得 (画像の中心)
        x, y = 640, 360  # 1280x720画像の中心
        distance = result_frame.get_distance(x, y)

        # 距離情報をカラースケール画像に変換する
        depth_color_frame = rs.colorizer().colorize(result_frame)
        depth_image_colored = np.asanyarray(depth_color_frame.get_data())

        # 表示
        cv2.putText(color_image, f"Distance at center: {distance:.2f} meters", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow('Color Frame', color_image)
        cv2.imshow('Depth Frame', depth_image_colored)

        # 'q'で終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    pipe.stop()
    cv2.destroyAllWindows()
