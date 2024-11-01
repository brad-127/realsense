def angle_translation(angle):
    # Normalize angle to be within [-180, 180] degrees
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle
