import pyrealsense2 as rs
import numpy as np
import cv2

# Create a config object
config = rs.config()

# Enable the depth and color streams
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Create a pipeline object
pipeline = rs.pipeline()

# Start the pipeline with the configured streams
profile = pipeline.start(config)

try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert depth frame to numpy array
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        # Scale the depth values to fit within the range of the colormap
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Display the resulting images
        cv2.namedWindow('Color Image', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Color Image', color_image)

        cv2.namedWindow('Depth Image', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Depth Image', depth_colormap)
        print("aaaaaa")
        # Press esc to exit
        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    # Stop streaming
    pipeline.stop()
    cv2.destroyAllWindows()
