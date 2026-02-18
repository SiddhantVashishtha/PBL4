import threading
import pyautogui

# --- Constants ---

# Screen
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Tracking
DEFAULT_SMOOTHING = 0.5
DEFAULT_CLICK_THRESHOLD = 0.05
DEFAULT_SCROLL_THRESHOLD = 0.05
DEFAULT_MARGIN = 0.15

# Camera
CAMERA_INDEX = 0

# Colors (BGR for OpenCV)
COLOR_TEXT = (255, 255, 255)
COLOR_HAND = (0, 255, 0)

# Gestures
GESTURE_NONE = "None"
GESTURE_PINCH = "Click (Pinch)"
GESTURE_SCROLL = "Scroll"

# --- Shared State ---

class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        
        # Tracking Data
        self.frame = None  # The latest processed frame (BGR)
        self.landmarks = None # MediaPipe landmarks
        self.hand_detected = False
        
        # Cursor Control
        self.cursor_active = True
        self.is_calibrating = False
        
        # Dynamic Settings
        self.smoothing_alpha = DEFAULT_SMOOTHING
        self.click_threshold = DEFAULT_CLICK_THRESHOLD
        self.margin = DEFAULT_MARGIN
        
        # UI Feedback
        self.current_gesture = GESTURE_NONE
        self.fps = 0.0
        

        
        # Calibration State
        self.calibration_step = 0
        self.calibration_message = ""

    def update_frame(self, frame):
        with self.lock:
            self.frame = frame
            
    def set_landmarks(self, landmarks):
        with self.lock:
            self.landmarks = landmarks
            
    def get_landmarks(self):
        with self.lock:
            return self.landmarks

    def get_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def set_gesture(self, gesture_name):
        with self.lock:
            self.current_gesture = gesture_name

    def get_gesture(self):
        with self.lock:
            return self.current_gesture

    def set_hand_detected(self, detected):
        with self.lock:
            self.hand_detected = detected

    def is_hand_detected(self):
        with self.lock:
            return self.hand_detected

    def set_fps(self, fps):
        with self.lock:
            self.fps = fps

    def get_fps(self):
        with self.lock:
            return self.fps

    def set_smoothing(self, alpha):
        with self.lock:
            self.smoothing_alpha = alpha

    def get_smoothing(self):
        with self.lock:
            return self.smoothing_alpha
            
    def set_click_threshold(self, threshold):
        with self.lock:
            self.click_threshold = threshold
            
    def set_margin(self, margin):
        with self.lock:
            self.margin = margin
            
    def get_margin(self):
        with self.lock:
            return self.margin

    def set_calibrating(self, is_calibrating):
        with self.lock:
            self.is_calibrating = is_calibrating

    def is_calibrating_active(self):
        with self.lock:
            return self.is_calibrating


