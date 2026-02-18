import time
import numpy as np
import mediapipe as mp
import threading

class CalibrationWizard:
    def __init__(self, shared_state, dashboard):
        self.state = shared_state
        self.dashboard = dashboard
        self.running = False
        self.mp_hands = mp.solutions.hands

    def run_calibration(self):
        if self.running:
            return
        self.running = True
        self.state.set_calibrating(True)
        
        try:
            # --- Step 1: Range Calibration ---
            self.state.calibration_message = "Step 1/3: Move hand FAR LEFT -> FAR RIGHT"
            time.sleep(2) 
            
            x_values = []
            start_time = time.time()
            while time.time() - start_time < 5.0: # 5 seconds
                landmarks = self.state.get_landmarks()
                if landmarks:
                    index_tip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    x_values.append(index_tip.x)
                time.sleep(0.05)
            
            if x_values:
                min_x = min(x_values)
                max_x = max(x_values)
                # Calculate margin (symmetric)
                # If min_x is 0.2 and max_x is 0.8, range is 0.6. Center is 0.5.
                # Margin should be roughly min_x.
                # Let's average the margins from both sides.
                margin_left = min_x
                margin_right = 1.0 - max_x
                new_margin = (margin_left + margin_right) / 2
                
                # Clamp margin for sanity (0.05 to 0.4)
                new_margin = max(0.05, min(0.4, new_margin))
                
                self.state.set_margin(new_margin)
                self.state.calibration_message = f"Range Set! Margin: {new_margin:.2f}"
            else:
                self.state.calibration_message = "Step 1 Failed: No hand detected"
            
            time.sleep(2)
            
            # --- Step 2: Pinch Calibration ---
            self.state.calibration_message = "Step 2/3: Pinch fingers naturally (Hold Pinch)"
            time.sleep(2)
            
            pinch_dists = []
            start_time = time.time()
            while time.time() - start_time < 4.0:
                landmarks = self.state.get_landmarks()
                if landmarks:
                    index_tip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    thumb_tip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                    dist = np.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
                    pinch_dists.append(dist)
                time.sleep(0.05)
                
            if pinch_dists:
                # Use the average of the smallest 50% of distances (assuming they were pinching most of the time)
                # Or just average.
                avg_dist = np.mean(pinch_dists)
                # Set threshold slightly higher than average pinch distance
                new_threshold = avg_dist * 1.3
                new_threshold = max(0.02, min(0.2, new_threshold)) # Sanity clamp
                
                self.state.set_click_threshold(new_threshold)
                self.state.calibration_message = f"Pinch Set! Threshold: {new_threshold:.3f}"
            else:
                 self.state.calibration_message = "Step 2 Failed: No hand detected"

            time.sleep(2)

            # --- Step 3: Stability Test ---
            self.state.calibration_message = "Step 3/3: Hold hand STEADY"
            time.sleep(2)
            
            stability_x = []
            start_time = time.time()
            while time.time() - start_time < 3.0:
                landmarks = self.state.get_landmarks()
                if landmarks:
                    index_tip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    stability_x.append(index_tip.x)
                time.sleep(0.05)
                
            if len(stability_x) > 10:
                variance = np.var(stability_x)
                # Low variance -> steady hand -> can handle higher Alpha (less smoothing)
                # High variance -> shaky -> needs lower Alpha (more smoothing)
                
                # Heuristic mapping:
                # Variance 0.00001 (very steady) -> Alpha 0.8
                # Variance 0.001 (shaky) -> Alpha 0.2
                
                # Log scale might be better but let's do linear interpolation
                # Target range 0.1 to 0.8
                # Input range ~0 to 0.0005?
                
                # Let's simpliy:
                # std_dev = sqrt(variance)
                std_dev = np.std(stability_x)
                
                # If std_dev < 0.002 -> Alpha 0.8
                # If std_dev > 0.01 -> Alpha 0.2
                
                target_alpha = np.interp(std_dev, [0.002, 0.01], [0.8, 0.2])
                self.state.set_smoothing(target_alpha)
                self.state.calibration_message = f"Stability Set! Alpha: {target_alpha:.2f}"
            else:
                self.state.calibration_message = "Step 3 Failed: Not enough data"

            time.sleep(2)
            self.state.calibration_message = "Calibration Complete!"
            time.sleep(2)

        except Exception as e:
            print(f"Calibration Error: {e}")
            self.state.calibration_message = f"Error: {str(e)[:20]}"
        finally:
            self.state.set_calibrating(False)
            self.state.calibration_message = ""
            self.running = False
