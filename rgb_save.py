import pyrealsense2 as rs
import numpy as np
import cv2
import os
from datetime import datetime


class RealSenseCapture:
    def __init__(self, output_dir="image_data", roi_top_left=(140, 60), roi_bottom_right=(500, 420),
                 resolution=(640, 480), depth_scale=0.03, frame_rate=30, camera_ids=[0,1]):  # ids=[0, 1]

        """
        複数のRealSenseカメラからRGBとDepth画像を取得し、指定されたディレクトリに保存するクラス
        :param output_dir: 出力ディレクトリ（デフォルト: "image_data"）
        :param roi_top_left: ROIの左上座標 (デフォルト: (140, 60))
        :param roi_bottom_right: ROIの右下座標 (デフォルト: (500, 420))
        :param resolution: 解像度 (デフォルト: (640, 480))
        :param depth_scale: 深度画像のスケール (デフォルト: 0.03)
        :param frame_rate: フレームレート (デフォルト: 30fps)
        :param camera_ids: 使用するカメラのIDリスト（デフォルト: [0, 1]）
        """
        self.camera_ids = camera_ids
        self.pipelines = []
        self.configs = []

        # 出力ディレクトリ設定
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # タイムスタンプ付きのサブディレクトリ作成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.timestamp_dir = os.path.join(self.output_dir, timestamp)
        os.makedirs(self.timestamp_dir, exist_ok=True)

        # 'img'と'data'のサブディレクトリを作成
        self.img_dir = os.path.join(self.timestamp_dir, "img")
        self.data_dir = os.path.join(self.timestamp_dir, "data")
        os.makedirs(self.img_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

        # ROI設定
        self.roi_top_left = roi_top_left
        self.roi_bottom_right = roi_bottom_right

        # カメラごとにパイプラインを設定
        for camera_id in self.camera_ids:
            config = rs.config()
            try:
                # カメラIDを指定してデバイスを有効化
                config.enable_device(str(camera_id))
                config.enable_stream(rs.stream.depth, resolution[0], resolution[1], rs.format.z16, frame_rate)
                config.enable_stream(rs.stream.color, resolution[0], resolution[1], rs.format.bgr8, frame_rate)
                self.configs.append(config)
                pipeline = rs.pipeline()
                pipeline.start(config)
                self.pipelines.append(pipeline)
                print(f"Camera {camera_id} started successfully.")
            except Exception as e:
                print(f"Error with camera {camera_id}: {e}")

        # 初期フレーム番号
        self.frame_num = 0


        def capture_and_return(self):
            """
            フレームを取得して、画像データを返す
            """
            self.frame_num += 1

            frames_list = []
            for pipeline in self.pipelines:
                frames = pipeline.wait_for_frames()
                frames_list.append(frames)

            rgb_frames = []
            depth_frames = []
            # 各カメラからRGBとDepth画像を取得
            for i, frames in enumerate(frames_list):
                color_frame = frames.get_color_frame()
                depth_frame = frames.get_depth_frame()

                # 画像データをNumPy配列に変換
                color_image = np.asanyarray(color_frame.get_data())
                depth_image = np.asanyarray(depth_frame.get_data())

                # ROIを切り出し
                roi_color = color_image[self.roi_top_left[1]:self.roi_bottom_right[1], 
                                        self.roi_top_left[0]:self.roi_bottom_right[0]]
                roi_depth = depth_image[self.roi_top_left[1]:self.roi_bottom_right[1], 
                                        self.roi_top_left[0]:self.roi_bottom_right[0]]

                # ROIを縦に反転
                roi_flipped = cv2.flip(roi_color, 0)
                resized_bgr = cv2.resize(roi_flipped, (160, 160))

                # BGRからRGBに変換
                resized_rgb = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2RGB)

                # 深度画像を160x160にリサイズ
                resized_depth = cv2.resize(roi_depth, (160, 160), interpolation=cv2.INTER_NEAREST)
                resized_depth_flipped = cv2.flip(resized_depth, 0)

                # RGBD画像を生成
                rgbd_image = np.dstack((resized_rgb, resized_depth_flipped))

                rgb_frames.append(resized_bgr)
                depth_frames.append(resized_depth_flipped)

            return rgb_frames, depth_frames  # 画像データと深度データを返す