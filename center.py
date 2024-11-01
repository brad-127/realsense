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
pipeline.start(config)

try:
    while True:
        # Get frames
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        
        if not color_frame:
            continue

        # Convert to image
        color_image = np.asanyarray(color_frame.get_data())

        # 上下反転
        color_image = cv2.flip(color_image, 0)

        # Calculate the center coordinates
        center_y, center_x = color_image.shape[0] // 2, color_image.shape[1] // 2

        # Get the RGB value at the center
        center_rgb = color_image[center_y, center_x]

        # Convert RGB to HSV
        center_hsv = cv2.cvtColor(np.uint8([[center_rgb]]), cv2.COLOR_BGR2HSV)[0][0]


        # Prepare text to display
        rgb_text = f"RGB: {center_rgb[2]}, {center_rgb[1]}, {center_rgb[0]}"  # BGR format
        hsv_text = f"HSV: {center_hsv[0]}, {center_hsv[1]}, {center_hsv[2]}"

        # Put text on the image in red
        cv2.putText(color_image, rgb_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)  # Red text
        cv2.putText(color_image, hsv_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)  # Red text
        
        # Print RGB and HSV values to the console
        print(f"\rRGB: {center_rgb[2]}, {center_rgb[1]}, {center_rgb[0]}   HSV: {center_hsv[0]}, {center_hsv[1]}, {center_hsv[2]}", end="")  # BGR format
      
        # Draw a red dot at the center
        cv2.circle(color_image, (center_x, center_y), 5, (0, 0, 255), -1)  # Red point

        # Show the image
        cv2.imshow("Color Image", color_image)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Stop the pipeline
    pipeline.stop()
    cv2.destroyAllWindows()
