import pyrealsense2 as rs
import numpy as np
import cv2
import os
from datetime import datetime


class RealSenseCapture:


    def __init__(self, output_dir="image_data", roi_top_left=(140, 60), roi_bottom_right=(500, 420),
                 resolution=(640, 480), depth_scale=0.03, frame_rate=30, camera_ids=[0, 1]):
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
            config.enable_device(str(camera_id))  # カメラIDを指定してデバイスを有効化
            config.enable_stream(rs.stream.depth, resolution[0], resolution[1], rs.format.z16, frame_rate)
            config.enable_stream(rs.stream.color, resolution[0], resolution[1], rs.format.bgr8, frame_rate)
            self.configs.append(config)
            pipeline = rs.pipeline()
            pipeline.start(config)
            self.pipelines.append(pipeline)

        # 初期フレーム番号
        self.frame_num = 0

    def capture_and_save(self):
        """
        フレームを取得して、指定されたディレクトリに保存する処理を行います
        """
        self.frame_num += 1

        frames_list = []
        for pipeline in self.pipelines:
            frames = pipeline.wait_for_frames()
            frames_list.append(frames)

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

            # 深度画像のカラーマップを適用
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(resized_depth_flipped, alpha=0.03), cv2.COLORMAP_JET)

            # RGBD画像を生成
            rgbd_image = np.dstack((resized_rgb, resized_depth_flipped))

            # フレームを表示
            cv2.imshow(f"RGB Image - Camera {i}", resized_bgr)
            cv2.imshow(f"Depth Image - Camera {i}", depth_colormap)

            # 画像を保存
            rgb_filename = os.path.join(self.img_dir, f"camera_{i}_rgb_frame_{self.frame_num:04d}.png")
            depth_filename = os.path.join(self.img_dir, f"camera_{i}_depth_frame_{self.frame_num:04d}.png")
            cv2.imwrite(rgb_filename, resized_bgr)
            cv2.imwrite(depth_filename, depth_colormap)

            # RGBDデータを.npyファイルとして保存
            rgbd_filename = os.path.join(self.data_dir, f"camera_{i}_rgbd_frame_{self.frame_num:04d}.npy")
            np.save(rgbd_filename, rgbd_image)

        print(f"\rFrame {self.frame_num}", end="")

    def stop(self):
        """ パイプラインを停止し、リソースを解放する """
        for pipeline in self.pipelines:
            pipeline.stop()
        cv2.destroyAllWindows()
        print("Pipeline stopped and resources released.")


>>>>>>> 82a450d (class for LF 10DoF)
