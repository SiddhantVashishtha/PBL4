import sys
import os

with open('debug_output_2.txt', 'w') as f:
    try:
        import mediapipe as mp
        f.write(f"import mediapipe successful\n")
    except ImportError as e:
        f.write(f"import mediapipe failed: {e}\n")

    try:
        from mediapipe.python import solutions
        f.write(f"from mediapipe.python import solutions successful\n")
        f.write(f"solutions.hands: {solutions.hands}\n")
    except ImportError as e:
        f.write(f"from mediapipe.python import solutions failed: {e}\n")

    try:
        import mediapipe.python as mp_python
        f.write(f"import mediapipe.python successful\n")
        f.write(f"dir(mp_python): {dir(mp_python)}\n")
    except ImportError as e:
        f.write(f"import mediapipe.python failed: {e}\n")
