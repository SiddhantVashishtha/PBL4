import tkinter as tk
import sys
import threading
from config import SharedState
from tracker import HandTracker
from dashboard import Dashboard

def main():
    print("Initializing Hand Tracking System...")
    
    # Initialize Shared State
    state = SharedState()
    
    # Start Tracking Thread
    tracker = HandTracker(state)
    tracker.start()
    print("Tracker thread started.")
    
    try:
        # Start Dashboard (Main UI Thread)
        app = Dashboard(state)
        
        # Override the close button behavior to ensure clean shutdown
        def on_limitless_void():
            print("Shutting down...")
            tracker.stop()
            app.destroy()
            
        app.protocol("WM_DELETE_WINDOW", on_limitless_void)
        
        print("Dashboard launched.")
        app.mainloop()
        
    except KeyboardInterrupt:
        print("Keyboard Interrupt detected.")
    finally:
        print("Cleaning up...")
        if tracker.is_alive():
            tracker.stop()
            tracker.join(timeout=2.0)
        sys.exit(0)

if __name__ == "__main__":
    main()
