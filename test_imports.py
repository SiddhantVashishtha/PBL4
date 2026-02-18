try:
    with open('verify_output.txt', 'w') as f:
        import cv2
        import mediapipe as mp
        import pyautogui
        import numpy
        f.write("Core dependencies imported successfully.\n")
        
        import tracker
        f.write("tracker imported successfully.\n")
        
        import main
        f.write("main imported successfully.\n")
        
except ImportError as e:
    with open('verify_output.txt', 'w') as f:
        f.write(f"Import failed: {e}\n")
except Exception as e:
    with open('verify_output.txt', 'w') as f:
        f.write(f"An error occurred: {e}\n")
