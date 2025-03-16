import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from collections import deque
import time
import platform

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
GREEN = (0, 255, 0)
RED = (0, 0, 255)

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

def draw_fullscreen_crosshair(frame, x, y, color):
    """Draw crosshair across the entire screen in OpenCV frame."""
    frame_height, frame_width, _ = frame.shape
    cv2.line(frame, (x, 0), (x, frame_height), color, 2)  # Vertical line
    cv2.line(frame, (0, y), (frame_width, y), color, 2)  # Horizontal line

def main():
    is_dragging = False

    print(f"Running on {SYSTEM} platform")
    if SYSTEM != 'Windows':
        print("Crosshair will be drawn in the camera feed instead of on the screen.")

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to capture frame from webcam")
            break

        current_cursor_x, current_cursor_y = pyautogui.position()
        frame = cv2.flip(frame, 1)  # Mirror effect for user experience
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb_frame)
        frame_height, frame_width, _ = frame.shape

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
                x = int(index_mcp.x * SCREEN_WIDTH)
                y = int(index_mcp.y * SCREEN_HEIGHT)

                smooth_x, smooth_y = get_smoothed_coordinates(x, y)
                print(f"Hand position - X: {smooth_x:.2f}, Y: {smooth_y:.2f}")

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

                # Draw fullscreen crosshair on OpenCV frame
                draw_fullscreen_crosshair(frame, int(index_mcp.x * frame_width), int(index_mcp.y * frame_height), color)

        # Display the frame
        cv2.imshow('Hand Mouse Controller', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.002)  # Reduced sleep for higher responsiveness

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 

    