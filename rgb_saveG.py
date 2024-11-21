import time
import pyrealsense2 as rs
import numpy as np
import cv2
import os
from datetime import datetime

class RealSenseCapture:
    def __init__(self, output_dir="image_data", roi_top_left=(140, 60), roi_bottom_right=(500, 420),
                 resolution=(640, 480), depth_scale=0.03, frame_rate=30):
        """
        Initializes the RealSense camera, configures streams, and sets up directories for saving images.
        :param output_dir: Output directory (default: "image_data")
        :param roi_top_left: Top-left coordinates of ROI (default: (140, 60))
        :param roi_bottom_right: Bottom-right coordinates of ROI (default: (500, 420))
        :param resolution: Image resolution (default: (640, 480))
        :param depth_scale: Depth image scale (default: 0.03)
        :param frame_rate: Frame rate (default: 30fps)
        """
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        # ROI settings
        self.roi_top_left = roi_top_left
        self.roi_bottom_right = roi_bottom_right

        # RealSense pipeline configuration
        self.config.enable_stream(rs.stream.depth, resolution[0], resolution[1], rs.format.z16, frame_rate)
        self.config.enable_stream(rs.stream.color, resolution[0], resolution[1], rs.format.bgr8, frame_rate)
        self.pipeline.start(self.config)
        print("[DEBUG] RealSense camera initialized and started.")

    def capture_and_return(self):
        """
        Capture frames and return RGB and Depth images after applying ROI and preprocessing.
        """
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()


        if not color_frame or not depth_frame:
            print("[ERROR] Failed to capture frames from RealSense camera.")
            return None, None

        # Convert to NumPy arrays
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        print(f"[DEBUG] Depth image min: {np.min(depth_image)}, max: {np.max(depth_image)}")


        # Apply ROI cropping
        roi_color = color_image[self.roi_top_left[1]:self.roi_bottom_right[1], 
                                self.roi_top_left[0]:self.roi_bottom_right[0]]
        roi_depth = depth_image[self.roi_top_left[1]:self.roi_bottom_right[1], 
                                self.roi_top_left[0]:self.roi_bottom_right[0]]
        


        # Flip the ROI vertically
        roi_flipped = cv2.flip(roi_color, 0)
        resized_bgr = cv2.resize(roi_flipped, (160, 160))

        # Convert BGR to RGB
        resized_rgb = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2RGB)

        # Resize depth image
        resized_depth = cv2.resize(roi_depth, (160, 160), interpolation=cv2.INTER_NEAREST)
        resized_depth_flipped = cv2.flip(resized_depth, 0)

        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(resized_depth_flipped, alpha=0.03), cv2.COLORMAP_JET)
        # cv2.imshow("Depth Colormap", depth_colormap)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return resized_rgb, depth_colormap, resized_rgb, resized_depth_flipped
 
    def show_image(self):
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        if not color_frame:
            print("[ERROR] Failed to capture frames from RealSense camera.")
            return None, None

        # Convert to NumPy arrays
        color_image = np.asanyarray(color_frame.get_data())

        # Apply ROI cropping
        roi_color = color_image[self.roi_top_left[1]:self.roi_bottom_right[1], 
                                self.roi_top_left[0]:self.roi_bottom_right[0]]
        
        # Flip the ROI vertically
        roi_flipped = cv2.flip(roi_color, 0)

        # Convert BGR to RGB
        resized_rgb = cv2.cvtColor(roi_flipped, cv2.COLOR_BGR2RGB)

        return resized_rgb
        
    # def save_images(self, rgb_image, depth_image):
    #     """
    #     Save the captured RGB and depth images.
    #     :param rgb_image: RGB image to be saved
    #     :param depth_image: Depth image to be saved
    #     """
    #     #img_dir = "data" #あとでコメントアウト
    #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    #     rgb_filename = os.path.join(self.img_dir, f"rgb_{timestamp}.png")
    #     depth_filename = os.path.join(self.img_dir, f"depth_{timestamp}.png")

    #     # Save the RGB and depth images
    #     cv2.imwrite(rgb_filename, rgb_image)
    #     cv2.imwrite(depth_filename, depth_image)
    #     print(f"[DEBUG] Saved RGB image to: {rgb_filename}")
    #     print(f"[DEBUG] Saved depth image to: {depth_filename}")

# if __name__ == "__main__":
#     # Example usage of RealSenseCapture
#     print("[DEBUG] Starting RealSenseCapture process...")
#     realsense_capture = RealSenseCapture()

#     try:
#         while True:
#             rgb_image, depth_image = realsense_capture.capture_and_return()
#             if rgb_image is not None and depth_image is not None:
#                 realsense_capture.save_images(rgb_image, depth_image)
#             time.sleep(1)  # Capture every second (adjust as needed)
#     except KeyboardInterrupt:
#         print("[DEBUG] Stopping RealSenseCapture process.")
#     finally:
#         print("[DEBUG] RealSenseCapture process completed.")