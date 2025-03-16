import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from collections import deque
import time
import platform
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

# Identify OS
SYSTEM = platform.system()

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# Initialize webcam
cap = cv2.VideoCapture(0)

# Get screen size
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Configure PyAutoGUI
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.001

# Moving average filter for smoothing
SMOOTHING_BUFFER_SIZE = 5
x_buffer = deque(maxlen=SMOOTHING_BUFFER_SIZE)
y_buffer = deque(maxlen=SMOOTHING_BUFFER_SIZE)

# Constants for crosshair
GREEN = "#00FF00"
RED = "#FF0000"

class TransparentWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes("-alpha", 0.5)  # Set window transparency
        self.root.attributes("-topmost", True)  # Keep window on top
        self.root.attributes("-fullscreen", True)
        self.root.overrideredirect(True)  # Remove window decorations
        
        # Make window transparent
        self.root.config(bg='systemTransparent')
        self.root.attributes("-transparent", True)
        
        # Create canvas for drawing
        self.canvas = tk.Canvas(
            self.root,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            highlightthickness=0,
            bg='systemTransparent'
        )
        self.canvas.pack()
        
    def update_crosshair(self, x, y, color):
        self.canvas.delete("all")
        # Draw vertical line
        self.canvas.create_line(x, 0, x, SCREEN_HEIGHT, fill=color, width=2)
        # Draw horizontal line
        self.canvas.create_line(0, y, SCREEN_WIDTH, y, fill=color, width=2)
        self.root.update()

def get_smoothed_coordinates(x, y):
    """Apply moving average filter to coordinates."""
    x_buffer.append(x)
    y_buffer.append(y)
    return sum(x_buffer) / len(x_buffer), sum(y_buffer) / len(y_buffer)

def calculate_finger_distance(hand_landmarks):
    """Calculate distance between thumb tip and index finger tip."""
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    return np.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)

def is_hand_near_cursor(hand_x, hand_y, cursor_x, cursor_y, threshold=100):
    """Check if hand position is within threshold pixels of cursor position."""
    distance = np.sqrt((hand_x - cursor_x)**2 + (hand_y - cursor_y)**2)
    return distance < threshold

def main():
    is_dragging = False
    window = TransparentWindow()

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to capture frame from webcam")
            break

        current_cursor_x, current_cursor_y = pyautogui.position()
        frame = cv2.flip(frame, 1)  # Mirror effect for user experience
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
                x = int(index_mcp.x * SCREEN_WIDTH)
                y = int(index_mcp.y * SCREEN_HEIGHT)

                smooth_x, smooth_y = get_smoothed_coordinates(x, y)

                finger_distance = calculate_finger_distance(hand_landmarks)
                hand_closed = finger_distance < 0.1
                hand_near_cursor = is_hand_near_cursor(smooth_x, smooth_y, current_cursor_x, current_cursor_y)

                if hand_closed and (is_dragging or hand_near_cursor):
                    pyautogui.moveTo(smooth_x, smooth_y)
                    is_dragging = True
                    color = RED
                elif hand_near_cursor:
                    color = RED
                    is_dragging = False
                else:
                    color = GREEN
                    is_dragging = False

                # Update crosshair in transparent window
                window.update_crosshair(int(smooth_x), int(smooth_y), color)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.002)  # Reduced sleep for higher responsiveness

    cap.release()
    cv2.destroyAllWindows()
    window.root.destroy()

if __name__ == "__main__":
    main()
