import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from collections import deque
import time
import platform
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import serial
import random
import pyttsx3

# Set up serial communication
ser = serial.Serial('/dev/cu.usbmodem11201', 9600)  # Replace 'COM10' with your Arduino's port

# Allow time for the serial connection to initialize
time.sleep(2)

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

# Add after other initializations
engine = pyttsx3.init()
engine.setProperty('rate', 190)
engine.startLoop(False)  # For macOS

# Add these variables after other constants
COFFEE_BREAK_MIN = 5  # seconds
COFFEE_BREAK_MAX = 20  # seconds
last_coffee_time = time.time()
coffee_break_interval = random.uniform(COFFEE_BREAK_MIN, COFFEE_BREAK_MAX)
is_coffee_break = False
coffee_break_start = 0

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

def announce_coffee_break():
    """Announce the coffee break"""
    try:
        engine.say("I'm taking a coffee break. Be back in 5 minutes.")
        engine.iterate()
    except:
        print("Failed to announce coffee break")

def main():
    global last_coffee_time, coffee_break_interval, is_coffee_break, coffee_break_start
    is_dragging = False
    window = TransparentWindow()

    while True:
        # Check if it's time for a coffee break
        current_time = time.time()
        if not is_coffee_break and (current_time - last_coffee_time) > coffee_break_interval:
            is_coffee_break = True
            coffee_break_start = current_time
            announce_coffee_break()
            # Set new random interval for next break
            coffee_break_interval = random.uniform(COFFEE_BREAK_MIN, COFFEE_BREAK_MAX)
            last_coffee_time = current_time
        
        # Check if coffee break is over (actual break is 5 seconds, not 5 minutes)
        if is_coffee_break and (current_time - coffee_break_start) > 5:
            is_coffee_break = False

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

                # Only move cursor if not on coffee break
                if not is_coffee_break and hand_closed and (is_dragging or hand_near_cursor):
                    pyautogui.moveTo(smooth_x, smooth_y)
                    is_dragging = True
                    color = RED
                elif hand_near_cursor:
                    color = RED
                    is_dragging = False
                else:
                    color = GREEN
                    is_dragging = False

                # Update crosshair color to indicate coffee break
                if is_coffee_break:
                    color = "#8B4513"  # Coffee brown!

                # Update crosshair in transparent window
                window.update_crosshair(int(smooth_x), int(smooth_y), color)

                ser.write(f"{x},{y}\n".encode())

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.002)  # Reduced sleep for higher responsiveness

    cap.release()
    cv2.destroyAllWindows()
    window.root.destroy()

if __name__ == "__main__":
    main()
