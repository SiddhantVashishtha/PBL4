import mediapipe as mp
import time
import math
import numpy as np

# Inherit constants
from config import GESTURE_PINCH, GESTURE_NONE

class GestureEngine:
    def __init__(self, shared_state):
        self.state = shared_state
        self.mp_hands = mp.solutions.hands
        
        # Cursor Smoothing State
        self.prev_x = 0
        self.prev_y = 0
        
    def _dist(self, p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def is_finger_extended(self, landmarks, finger_tip_idx, finger_dip_idx):
        # A simple check: if tip is higher (smaller y) than DIP joint
        # Note: This simple logic assumes hand is upright. 
        # For more robustness, we can check distance from wrist.
        return landmarks[finger_tip_idx].y < landmarks[finger_dip_idx].y

    def is_folded(self, landmarks, finger_tip_idx, finger_pip_idx):
        # Tip is below PIP (or closer to wrist than PIP)
        # Using distance to wrist is often more reliable for rotation
        wrist = landmarks[self.mp_hands.HandLandmark.WRIST]
        tip_dist = self._dist(landmarks[finger_tip_idx], wrist)
        pip_dist = self._dist(landmarks[finger_pip_idx], wrist)
        return tip_dist < pip_dist



    def is_pinch(self, landmarks):
        # Index tip and Thumb tip close
        INDEX_TIP = self.mp_hands.HandLandmark.INDEX_FINGER_TIP
        THUMB_TIP = self.mp_hands.HandLandmark.THUMB_TIP
        
        dist = self._dist(landmarks[INDEX_TIP], landmarks[THUMB_TIP])
        return dist < self.state.click_threshold

    def smooth_coordinates(self, x, y):
        alpha = self.state.get_smoothing()
        
        # Exponential Moving Average
        smooth_x = alpha * x + (1 - alpha) * self.prev_x
        smooth_y = alpha * y + (1 - alpha) * self.prev_y
        
        self.prev_x = smooth_x
        self.prev_y = smooth_y
        
        return int(smooth_x), int(smooth_y)
