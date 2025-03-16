import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from collections import deque
import keyboard
import time

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
    print(f"Distance to cursor: {distance}")  # Debug print
    return distance < threshold

def main():
    # Previous cursor position for drag detection
    is_dragging = False
    
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
                
                # Check for hand gesture (closed fist)
                finger_distance = calculate_finger_distance(hand_landmarks)
                print(f"Finger distance: {finger_distance}")  # Debug print
                
                # Check if hand is closed (fist) and near current cursor
                hand_closed = finger_distance < 0.1  # Adjust threshold as needed
                hand_near_cursor = is_hand_near_cursor(smooth_x, smooth_y, current_cursor_x, current_cursor_y, threshold=200)
                
                print(f"Hand closed: {hand_closed}, Hand near cursor: {hand_near_cursor}")  # Debug print
                
                if hand_closed:  # Simplified condition for testing
                    # Move cursor only when hand is closed
                    pyautogui.moveTo(smooth_x, smooth_y)
                    if not is_dragging:
                        print("Starting drag")  # Debug print
                        pyautogui.mouseDown()
                        is_dragging = True
                else:
                    if is_dragging:
                        print("Ending drag")  # Debug print
                        pyautogui.mouseUp()
                        is_dragging = False
                
                # Draw cursor position and debug info for visualization
                cv2.circle(frame, (int(index_mcp.x * frame_width), 
                                 int(index_mcp.y * frame_height)), 
                          10, (0, 255, 0), -1)
                
                # Draw debug text
                cv2.putText(frame, f"Finger distance: {finger_distance:.3f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Hand closed: {hand_closed}", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display the frame
        cv2.imshow('Hand Mouse Controller', frame)
        
        # Check for 'q' key press to quit
        if cv2.waitKey(1) & 0xFF == ord('q') or keyboard.is_pressed('q'):
            break
        
        # Small delay to prevent high CPU usage
        time.sleep(0.01)

    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    if is_dragging:
        pyautogui.mouseUp()

if __name__ == "__main__":
    main() 
