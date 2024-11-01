import pyrealsense2 as rs
import numpy as np
import cv2
import os
from datetime import datetime

# Create a config object
config = rs.config()

# Enable the depth and color streams
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Create a pipeline object
pipeline = rs.pipeline()

# Start the pipeline with the configured streams
profile = pipeline.start(config)

num = 0

# Create the main directory if it doesn't exist
main_dir = "image_data"
os.makedirs(main_dir, exist_ok=True)

# Create a subdirectory with the current timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
timestamp_dir = os.path.join(main_dir, timestamp)
os.makedirs(timestamp_dir, exist_ok=True)

# Create the 'rgb' and 'depth' subdirectories
img_dir = os.path.join(timestamp_dir, "img")
data_dir = os.path.join(timestamp_dir, "data")
os.makedirs(img_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

while True:
    # フレームの取得
    num += 1
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    depth_frame = frames.get_depth_frame()
    
    # convert to image
    color_image = np.asanyarray(color_frame.get_data())
    depth_image = np.asanyarray(depth_frame.get_data())
    
    ############ Define the region of interest (ROI) ############
    # (x, y) coordinates of the top-left and bottom-right corners of the ROI
    roi_top_left = (140, 60)
    roi_bottom_right = (500, 420)  # Adjusted to fit the frame size

    # Get the ROI from the color frame
    roi_color = color_image[roi_top_left[1]:roi_bottom_right[1], roi_top_left[0]:roi_bottom_right[0]]

    # Flip the ROI vertically
    roi_flipped = cv2.flip(roi_color, 0)

    # Resize to 160x160 pixels
    resized_bgr = cv2.resize(roi_flipped, (160, 160))

    # resized_bgr を BGR から HSV に変換
    resized_hsv = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2HSV)
    
    # H、S、Vを分割
    H, S, V = cv2.split(resized_hsv)

    # Hをラジアンに変換
    H_radians = H * 2 * (np.pi / 180.0)

    # cosθとsinθを計算
    cos_theta = np.cos(H_radians)
    sin_theta = np.sin(H_radians)

    modified_hsv = np.stack((cos_theta, sin_theta, S), axis=-1)


    # HSV を BGR に戻す
    print(f"\rresized_hsv:{resized_hsv[0][0]},result:{modified_hsv[0][0]},shape:{modified_hsv.shape}", end="")

    # Resize depth image to match the resized RGB image and flip it vertically
    roi_depth = depth_image[roi_top_left[1]:roi_bottom_right[1], roi_top_left[0]:roi_bottom_right[0]]
    resized_depth = cv2.resize(roi_depth, (160, 160), interpolation=cv2.INTER_NEAREST)
    resized_depth_flipped = cv2.flip(resized_depth, 0)  # Flip depth image vertically
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(resized_depth_flipped, alpha=0.03), cv2.COLORMAP_JET)
    
    # Create an RGBD image by stacking the RGB and depth channels
    rgbd_image = np.dstack((modified_hsv, resized_depth_flipped))

    # print(f"\rframe:{num}", end="")
    
    # Show the RGBD image
    cv2.imshow("RBG Image", resized_bgr)
    cv2.imshow("Depth Image", depth_colormap)

    # Save the images
    rgb_filename = os.path.join(img_dir, f"rgb_frame_{num:04d}.png")
    depth_filename = os.path.join(img_dir, f"depth_frame_{num:04d}.png")
    cv2.imwrite(rgb_filename, resized_bgr)
    cv2.imwrite(depth_filename, depth_colormap)

    # Save the RGBD data as a .npy file
    rgbd_filename = os.path.join(data_dir, f"rgbd_frame_{num:04d}.npy")
    np.save(rgbd_filename, rgbd_image)

    cv2.waitKey(500)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Stop the pipeline
pipeline.stop()
cv2.destroyAllWindows()
