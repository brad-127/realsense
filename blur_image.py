
=======
import pyrealsense2 as rs
>>>>>>> 353cbc0 (class for LF 10DoF)
import numpy as np
import cv2
import math
import angle_trans

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

# ぼかしの強さを調節する変数
blur_strength = 30

while True:
    # フレームの取得
    num += 1
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    depth_frame = frames.get_depth_frame()
    
    # convert to image
    color_image = np.asanyarray(color_frame.get_data())

    ############ Define the region of interest (ROI) ############
    # (x, y) coordinates of the top-left and bottom-right corners of the ROI
    roi_top_left = (0, 0)
    roi_bottom_right = (100000, 500000)

    # Draw a green rectangle to indicate the ROI
    cv2.rectangle(color_image, roi_top_left, roi_bottom_right, (0, 255, 0), 2)

    # Get the ROI from the color frame
    roi_color = color_image[roi_top_left[1]:roi_bottom_right[1], roi_top_left[0]:roi_bottom_right[0]]
    
    ############ Looking for brown box with HSV ############ 
    ##### convert BGR to HSV
    hsv_image = cv2.cvtColor(roi_color, cv2.COLOR_BGR2HSV)
    
    # parameter setting for finding "brown" in HSV
    # Hue (H) for brown
    lower_hsv = np.array([75, 70, 50])  # Hue, Saturation, Value lower bound
    upper_hsv = np.array([95, 255, 255])  # Hue, Saturation, Value upper bound
    
    # mask
    masked_image = cv2.inRange(hsv_image, lower_hsv, upper_hsv)

    ##### find rectangle
    contours, hierarchy = cv2.findContours(
        masked_image,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE
    )

    largest_area = 0

    for i, contour in enumerate(contours):
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.intp(box)

        # record the largest rectangle
        if largest_area < ((box[0][0] - box[1][0]) ** 2 + (box[0][1] - box[2][1]) ** 2):
            largest_area = ((box[0][0] - box[1][0]) ** 2 + (box[0][1] - box[2][1]) ** 2)
            largest_box = box

    ############ Calculate the target box coordination and angle ############ 
    if largest_area != 0:
        # Calculate the center of the target in the ROI
        target_box_center_1 = (largest_box[0][0] + largest_box[2][0]) // 2
        target_box_center_2 = (largest_box[0][1] + largest_box[2][1]) // 2

        #print(f"\rbox: {largest_box[0][0]}", end="")
        
        # Calculate the angle of the rotated rectangle

        # point 0 1 のx yの差を計算
        delta_x1 = largest_box[0][0] - largest_box[1][0]
        delta_y1 = largest_box[0][1] - largest_box[1][1]

        # point 1 2 のx yの差を計算
        delta_x2 = largest_box[1][0] - largest_box[2][0]
        delta_y2 = largest_box[1][1] - largest_box[2][1]

        if delta_x1**2+delta_y1**2 > delta_x2**2+delta_y2**2:
            delta_x = delta_x1
            delta_y = delta_y1
        else:
            delta_x = delta_x2
            delta_y = delta_y2

        # アークタンジェント関数を使用して角度を計算
        angle_rad = math.atan2(delta_y, delta_x)
        # 弧度法から度数法に変換
        angle = math.degrees(angle_rad)

        width = max(item[0] for item in largest_box)-min(item[0] for item in largest_box)
        height = max(item[1] for item in largest_box)-min(item[1] for item in largest_box)
        if width < height:
            print(f"\rangle:{angle} tate", end="")
        else:
            print(f"\rangle:{angle} yoko", end="")
        
        #angle_translation
        angle = angle_trans.angle_translation(angle)
 
        # Draw the center point on the ROI
        cv2.circle(roi_color, (target_box_center_1, target_box_center_2), 2, (0, 255, 0), 5)

        # Display the pixel coordinates and angle next to the point
        text = "Pixel X: {} Y: {} Angle: {:.2f} degrees".format(target_box_center_1, target_box_center_2, angle)
        cv2.putText(roi_color, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
        
        # Draw the detected box on the ROI
        cv2.drawContours(roi_color, [largest_box], 0, (0, 0, 255), 2)

    # Apply Gaussian blur to the ROI for darkening the surroundings
    blurred_roi_color = cv2.GaussianBlur(roi_color, (0, 0), blur_strength)
    mask = cv2.cvtColor(masked_image, cv2.COLOR_GRAY2BGR)
    result = cv2.addWeighted(blurred_roi_color, 1.5, mask, -0.5, 0)

    # Draw the box coordinates and the red box
    if largest_area != 0:
        cv2.drawContours(result, [largest_box], 0, (0, 0, 255), 2)
        
        # Add text to display the coordinates and angle
        text = "Pixel X: {} Y: {} Angle: {:.2f} degrees".format(target_box_center_1, target_box_center_2, angle)
        cv2.putText(result, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1, cv2.LINE_AA)

    # Display the image
    cv2.imshow("Image", result)
    cv2.waitKey(200)
