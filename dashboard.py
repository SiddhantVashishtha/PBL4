import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import threading

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_TEXT,
    GESTURE_NONE,
    GESTURE_NONE
)
from calibration import CalibrationWizard

class Dashboard(tk.Tk):
    def __init__(self, shared_state):
        super().__init__()
        self.state = shared_state
        
        self.title("Hand Tracking Control Center")
        self.geometry("400x600")
        self.resizable(False, False)
        
        # Style
        self.configure(bg="#2E2E2E")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TLabel", background="#2E2E2E", foreground="white", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10))
        self.style.configure("TFrame", background="#2E2E2E")
        
        # --- UI Components ---
        self.create_widgets()
        
        # Calibration Wizard
        self.calibration_wizard = CalibrationWizard(shared_state, self)
        
        # Main UI Loop for updates
        self.update_ui()

    def create_widgets(self):
        # Header
        header = ttk.Label(self, text="Hand Tracking Dashboard", font=("Segoe UI", 16, "bold"))
        header.pack(pady=10)
        
        # Stats Frame
        stats_frame = ttk.LabelFrame(self, text="Live Stats", padding=10)
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        self.fps_label = ttk.Label(stats_frame, text="FPS: 0.0")
        self.fps_label.pack(anchor="w")
        
        self.gesture_label = ttk.Label(stats_frame, text="Gesture: None")
        self.gesture_label.pack(anchor="w")
        
        self.hand_label = ttk.Label(stats_frame, text="Hand Detected: NO", foreground="red")
        self.hand_label.pack(anchor="w")

        self.calibration_status_label = ttk.Label(stats_frame, text="", foreground="yellow")
        self.calibration_status_label.pack(anchor="w")
        
        # Controls Frame
        controls_frame = ttk.LabelFrame(self, text="Controls", padding=10)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Smoothing Slider
        ttk.Label(controls_frame, text="Smoothing (Alpha)").pack(anchor="w")
        self.smoothing_val_label = ttk.Label(controls_frame, text=f"{self.state.get_smoothing():.2f}")
        self.smoothing_val_label.pack(anchor="e")
        
        self.smoothing_slider = ttk.Scale(controls_frame, from_=0.1, to=0.9, orient="horizontal", command=self.on_smoothing_change)
        self.smoothing_slider.set(self.state.get_smoothing())
        self.smoothing_slider.pack(fill="x", pady=5)
        
        # Toggle Preview
        self.show_preview_var = tk.BooleanVar(value=False)
        self.preview_cb = ttk.Checkbutton(controls_frame, text="Show Camera Preview", variable=self.show_preview_var, command=self.toggle_preview)
        self.preview_cb.pack(anchor="w", pady=5)
        
        # Calibration Button
        self.cal_btn = ttk.Button(controls_frame, text="Run Calibration", command=self.start_calibration)
        self.cal_btn.pack(fill="x", pady=10)
        
        # Preview Frame
        self.preview_frame = tk.Frame(self, bg="black", width=320, height=240)
        self.preview_frame.pack(pady=10)
        self.preview_label = tk.Label(self.preview_frame, bg="black")
        self.preview_label.pack()

    def on_smoothing_change(self, val):
        alpha = float(val)
        self.state.set_smoothing(alpha)
        self.smoothing_val_label.config(text=f"{alpha:.2f}")

    def toggle_preview(self):
        if not self.show_preview_var.get():
            self.preview_label.config(image="")
            self.preview_label.image = None

    def start_calibration(self):
        if not self.state.is_calibrating_active():
            threading.Thread(target=self.calibration_wizard.run_calibration, daemon=True).start()

    def update_ui(self):
        # Update Stats
        fps = self.state.get_fps()
        self.fps_label.config(text=f"FPS: {fps:.1f}")
        
        gesture = self.state.get_gesture()
        self.gesture_label.config(text=f"Gesture: {gesture}")
        
        detected = self.state.is_hand_detected()
        self.hand_label.config(text="Hand Detected: YES" if detected else "Hand Detected: NO", foreground="green" if detected else "red")
        
        # Calibration Check
        if self.state.is_calibrating_active():
            self.cal_btn.state(["disabled"])
            self.calibration_status_label.config(text=self.state.calibration_message)
        else:
            self.cal_btn.state(["!disabled"])
            self.calibration_status_label.config(text="")

        # Gojo Easter Egg Check removed

        # Update Preview
        if self.show_preview_var.get():
            frame = self.state.get_frame()
            if frame is not None:
                # Resize for preview (320x240)
                frame = cv2.resize(frame, (320, 240))
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to PIL
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.preview_label.config(image=imgtk)
                self.preview_label.image = imgtk
        
        self.after(30, self.update_ui)

    def on_closing(self):
        self.state.set_calibrating(False) # Stop calibration if running
        self.destroy()

if __name__ == "__main__":
    # Test only
    pass
