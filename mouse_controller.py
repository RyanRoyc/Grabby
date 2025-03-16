import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from collections import deque
import time
import platform
import sys

# Import Windows-specific modules only on Windows
SYSTEM = platform.system()
if SYSTEM == 'Windows':
    import win32gui
    import win32con
    import win32api

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

# Add new constants for crosshair
CROSSHAIR_SIZE = 20
CROSSHAIR_THICKNESS = 2
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

    distance = np.sqrt(
        (thumb_tip.x - index_tip.x)**2 +
        (thumb_tip.y - index_tip.y)**2
    )
    return distance

def is_hand_near_cursor(hand_x, hand_y, cursor_x, cursor_y, threshold=100):
    """Check if hand position is within threshold pixels of cursor position."""
    distance = np.sqrt((hand_x - cursor_x)**2 + (hand_y - cursor_y)**2)
    return distance < threshold

def draw_screen_crosshair(x, y, color):
    """Draw crosshair directly on screen using OS-specific methods."""
    if SYSTEM == 'Windows':
        # Windows implementation using win32gui
        hdc = win32gui.GetDC(0)

        # Create pen for drawing
        if color == GREEN:
            pen = win32gui.CreatePen(win32con.PS_SOLID, CROSSHAIR_THICKNESS, win32api.RGB(0, 255, 0))
        else:  # RED
            pen = win32gui.CreatePen(win32con.PS_SOLID, CROSSHAIR_THICKNESS, win32api.RGB(255, 0, 0))

        old_pen = win32gui.SelectObject(hdc, pen)

        # Draw horizontal line
        win32gui.MoveToEx(hdc, x - CROSSHAIR_SIZE, y)
        win32gui.LineTo(hdc, x + CROSSHAIR_SIZE, y)

        # Draw vertical line
        win32gui.MoveToEx(hdc, x, y - CROSSHAIR_SIZE)
        win32gui.LineTo(hdc, x, y + CROSSHAIR_SIZE)

        # Clean up
        win32gui.SelectObject(hdc, old_pen)
        win32gui.DeleteObject(pen)
        win32gui.ReleaseDC(0, hdc)
    else:
        # For macOS and Linux, we'll skip drawing on the screen directly
        # because it requires different system-specific libraries
        # Cursor movement will still work, but without the crosshair
        pass

def main():
    is_dragging = False

    # Print system information
    print(f"Running on {SYSTEM} platform")
    if SYSTEM != 'Windows':
        print("Note: Crosshair drawing is only supported on Windows")

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to capture frame from webcam")
            break

        # Get current cursor position
        current_cursor_x, current_cursor_y = pyautogui.position()

        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame and detect hands
        results = hands.process(rgb_frame)

        frame_height, frame_width, _ = frame.shape

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get index finger MCP joint coordinates
                index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]

                # Convert normalized coordinates to screen coordinates
                x = int(index_mcp.x * SCREEN_WIDTH)
                y = int(index_mcp.y * SCREEN_HEIGHT)

                # Apply smoothing
                smooth_x, smooth_y = get_smoothed_coordinates(x, y)

                # Print coordinates
                print(f"Hand position - X: {smooth_x:.2f}, Y: {smooth_y:.2f}")

                # Check for hand gesture (closed fist)
                finger_distance = calculate_finger_distance(hand_landmarks)
                hand_closed = finger_distance < 0.1

                # Check if hand is near current cursor
                hand_near_cursor = is_hand_near_cursor(smooth_x, smooth_y,
                                                     current_cursor_x, current_cursor_y)

                # Determine if we should start/continue dragging
                if hand_closed and (is_dragging or hand_near_cursor):
                    pyautogui.moveTo(smooth_x, smooth_y)
                    is_dragging = True
                    color = RED
                elif hand_near_cursor:
                    # Hand is near cursor but not closed - show ready to drag
                    color = RED
                    is_dragging = False
                else:
                    # Hand is neither dragging nor near cursor
                    color = GREEN
                    is_dragging = False

                # Draw crosshair on screen (only works on Windows)
                if SYSTEM == 'Windows':
                    draw_screen_crosshair(int(smooth_x), int(smooth_y), color)

                # Draw cursor position for visualization in camera feed
                cv2.circle(frame, (int(index_mcp.x * frame_width),
                                 int(index_mcp.y * frame_height)),
                          10, color, -1)

        # Display the frame
        cv2.imshow('Hand Mouse Controller', frame)

        # Check for 'q' key press to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Smaller delay for higher responsiveness
        time.sleep(0.005)

    # Clean up
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
