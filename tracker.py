import cv2
import mediapipe as mp
import threading
import pyautogui
import time
import numpy as np

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    CAMERA_INDEX,
    COLOR_HAND,
    GESTURE_NONE, GESTURE_PINCH, GESTURE_SCROLL
)
from gestures import GestureEngine

class HandTracker(threading.Thread):
    def __init__(self, shared_state):
        super().__init__()
        self.state = shared_state
        self.daemon = True # Ensure thread stops when main thread exits
        self.running = True
        
        # MediaPipe Setup
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            model_complexity=1
        )
        
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.gesture_engine = GestureEngine(shared_state)
        
        # Performance monitoring
        self.prev_time = 0
        
        # Cursor State
        self.mouse_pressed = False
        
    def run(self):
        while self.running and self.cap.isOpened():
            success, image = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # Flip the image horizontally for a later selfie-view display
            # Convert the BGR image to RGB.
            image = cv2.flip(image, 1)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image_rgb.flags.writeable = False
            results = self.hands.process(image_rgb)

            # Draw the hand annotations on the image.
            image_rgb.flags.writeable = True
            image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR) # Convert back for display/processing logic if needed
            
            h, w, _ = image.shape
            
            current_gesture = GESTURE_NONE
            hand_detected = False

            if results.multi_hand_landmarks:
                hand_detected = True
                for hand_landmarks in results.multi_hand_landmarks:
                    # Update Shared State with landmarks for Calibration/Dashboard
                    self.state.set_landmarks(hand_landmarks)

                    # Draw landmarks on debug frame
                    self.mp_draw.draw_landmarks(
                        image,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_draw.DrawingSpec(color=COLOR_HAND, thickness=2, circle_radius=2),
                        self.mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2)
                    )
                    
                    # 1. Gesture Detection
                    
                    current_gesture = GESTURE_NONE

                    # Shared State Update Logic for Gesture
                    if current_gesture != GESTURE_NONE:
                        pass # Keep it set
                    
                    # 2. Movement Logic (Index Finger Tip)
                    if self.state.cursor_active and not self.state.is_calibrating_active():
                        # Get Index Finger Tip
                        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                        
                        # Convert to screen coordinates
                        margin = self.state.get_margin() # Dynamic Margin
                        
                        # Use numpy interp to map camera coords -> screen coords
                        target_x = np.interp(index_tip.x, (margin, 1-margin), (0, SCREEN_WIDTH))
                        target_y = np.interp(index_tip.y, (margin, 1-margin), (0, SCREEN_HEIGHT))
                        
                        # Smoothing
                        final_x, final_y = self.gesture_engine.smooth_coordinates(target_x, target_y)
                        
                        # Apply limits
                        final_x = max(0, min(SCREEN_WIDTH - 1, final_x))
                        final_y = max(0, min(SCREEN_HEIGHT - 1, final_y))
                        
                        pyautogui.moveTo(final_x, final_y, _pause=False)
                        
                        # 3. Click Logic (Pinch)
                        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                        
                        dist = np.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
                        
                        # Logic: if distance < threshold -> Click
                        if dist < self.state.click_threshold:
                            if not self.mouse_pressed:
                                pyautogui.mouseDown()
                                self.mouse_pressed = True
                                current_gesture = GESTURE_PINCH
                        else:
                            if self.mouse_pressed:
                                pyautogui.mouseUp()
                                self.mouse_pressed = False
            else:
                self.state.set_landmarks(None) # Clear landmarks
                if self.mouse_pressed:
                    pyautogui.mouseUp()
                    self.mouse_pressed = False
            
            # FPS Calculation
            curr_time = time.time()
            fps = 1 / (curr_time - self.prev_time) if self.prev_time != 0 else 0
            self.prev_time = curr_time
            
            # Update Shared State
            self.state.update_frame(image)
            self.state.set_hand_detected(hand_detected)
            if current_gesture != GESTURE_NONE:
                 self.state.set_gesture(current_gesture)
            elif hand_detected and self.mouse_pressed:
                 self.state.set_gesture(GESTURE_PINCH)
            elif hand_detected:
                 self.state.set_gesture(GESTURE_NONE)
            else:
                 self.state.set_gesture("No Hand")
                 
            self.state.set_fps(fps)
            
            time.sleep(0.001)

    def stop(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        self.hands.close()
