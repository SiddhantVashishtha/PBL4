import cv2
import threading
import time

def play_video(file_path):
    def _run():
        try:
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                print(f"Error: Could not open video {file_path}")
                return

            window_name = "Dominion Expansion: Unlimited Void"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                cv2.imshow(window_name, frame)
                
                # Check for 'q' or Esc to close early, though usually we play till end
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
        except Exception as e:
            print(f"Error playing video: {e}")

    # Run in a separate thread so it doesn't block the tracker or UI
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
