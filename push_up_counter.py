import cv2
import mediapipe as mp
import math
import time

# Initialize MediaPipe Pose Model
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initialize video capture
cap = cv2.VideoCapture(0)

# Variables to track push-up count
push_ups = 0
is_pushing_up = False
last_push_up_time = 0  # To track the last push-up time
push_up_pause = 0.5  # Minimum time (in seconds) to pause before counting again (to avoid multiple counts at the bottom)

def calculate_angle(a, b, c):
    """Calculate the angle between three points"""
    angle = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    )
    if angle < 0:
        angle += 360
    return angle

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame for a more intuitive mirror view
    frame = cv2.flip(frame, 1)

    # Convert frame to RGB (MediaPipe needs RGB)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    # Check if pose landmarks are detected
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # Get the coordinates for the shoulder, elbow, and wrist (left side)
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y]

        # Calculate the angle between the shoulder, elbow, and wrist
        angle = calculate_angle(shoulder, elbow, wrist)

        # Display the angle on the frame
        cv2.putText(frame, f'Angle: {int(angle)}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Push-up detection logic
        if angle > 160:  # Arm extended (Top position)
            if not is_pushing_up:
                # Check if enough time has passed to count another push-up
                if time.time() - last_push_up_time > push_up_pause:
                    push_ups += 1
                    last_push_up_time = time.time()  # Update the last push-up time
                is_pushing_up = True
        elif angle < 90:  # Arm bent (Bottom position)
            if is_pushing_up:
                # We don't count again at the bottom to avoid double counting
                is_pushing_up = False

    # Display the current push-up count
    cv2.putText(frame, f'Push-ups: {push_ups}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Render the landmarks on the image
    mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Show the frame
    cv2.imshow("Push-Up Counter", frame)

    # Exit if the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
