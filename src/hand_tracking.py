# hand_tracking.py (Final Fix - Simple & Reliable Camera Logic)

import cv2
import mediapipe as mp
import math
from collections import deque
from config import *

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=MAX_HANDS,
            min_detection_confidence=MIN_DETECTION_CONF,
            min_tracking_confidence=MIN_TRACKING_CONF
        )
        self.dx_queue = deque(maxlen=SMOOTH_FACTOR)
        self.dy_queue = deque(maxlen=SMOOTH_FACTOR)

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)
        left = None
        right = None
        if result.multi_hand_landmarks and result.multi_handedness:
            for lm, handness in zip(result.multi_hand_landmarks, result.multi_handedness):
                if handness.classification[0].label == "Left":
                    left = lm.landmark
                else:
                    right = lm.landmark
        return left, right

    def fingers_status(self, landmarks):
        tips = [4, 8, 12, 16, 20]
        status = []
        status.append(1 if landmarks[tips[0]].x < landmarks[tips[0] - 1].x else 0)
        for i in range(1, 5):
            status.append(1 if landmarks[tips[i]].y < landmarks[tips[i] - 2].y else 0)
        return status

    def is_thumb_pointing_left(self, landmarks):
        return landmarks[4].x < landmarks[2].x - 0.04

    def is_thumb_pointing_right(self, landmarks):
        return landmarks[4].x > landmarks[2].x + 0.04

    def is_thumb_down(self, landmarks):
        return landmarks[4].y > landmarks[3].y and landmarks[4].y > landmarks[2].y
    
    # --- FINAL RELIABLE CAMERA MOVEMENT METHOD ---
    def get_camera_rotation_delta(self, landmarks):
        """
        Calculates mouse movement delta with a dead zone and simple linear sensitivity.
        This is a robust and reliable method.
        """
        center_x, center_y = 0.5, 0.5
        # Use a stable landmark like the base of the middle finger
        hand_x, hand_y = landmarks[9].x, landmarks[9].y
        
        dx_raw = hand_x - center_x
        dy_raw = hand_y - center_y
        
        dx = 0
        dy = 0

        # Apply dead zone
        if abs(dx_raw) > DEAD_ZONE:
            dx = dx_raw
        
        if abs(dy_raw) > DEAD_ZONE:
            dy = dy_raw

        # Apply smoothing
        self.dx_queue.append(dx)
        self.dy_queue.append(dy)
        smooth_dx = sum(self.dx_queue) / len(self.dx_queue)
        smooth_dy = sum(self.dy_queue) / len(self.dy_queue)
        
        # Apply simple, linear sensitivity
        final_dx = int(CAM_SENS_X * smooth_dx)
        final_dy = int(CAM_SENS_Y * smooth_dy)
        
        return final_dx, final_dy
