import cv2
import mediapipe as mp
import math
import time
import pyttsx3
import random
import threading

# Initialize MediaPipe Pose Model
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust speaking rate

# Function to speak text in a non-blocking way
def speak_text(text):
    def speak():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=speak, daemon=True).start()

# Expanded snarky comments with different categories
FORM_COMMENTS = [
    "Is your chest allergic to the floor or something?",
    "That's not a push-up, that's just planking with extra wobbling",
    "I've seen better form in a wet noodle",
    "Are you trying to do push-ups or interpretive dance?",
    "Your form is so bad, it should be in an abstract art museum"
]

MOTIVATION_COMMENTS = [
    "My CPU gets more exercise running this program",
    "Even Windows updates are more productive than this",
    "You're moving with all the energy of a sleepy sloth",
    "Did you forget to charge your batteries this morning?",
    "Is this your first day having arms?"
]

COUNTING_COMMENTS = [
    "That's {count} push-ups... allegedly",
    "Push-up #{count}, or as I call it, a gravity-assisted chest bounce",
    "Wow, {count} already? Are you counting in binary?",
    "That's {count}... in your dreams maybe",
    "Let's generously call that {count} push-ups"
]

TIRED_COMMENTS = [
    "Taking a break already? I thought humans had endurance",
    "Oh good, a break. My facial recognition was getting bored",
    "Need a nap? I've only been watching for {duration} seconds",
    "My cooling fan gets more exercise than this",
    "I could render a 3D model of better push-ups in this time"
]

# Add variables for comment timing and variety
last_comment_time = 0
comment_cooldown = 5  # Seconds between comments
last_comment_type = None

# Initialize video capture
cap = cv2.VideoCapture(0)

# Variables to track push-up count
push_ups = 0
is_pushing_up = False
last_push_up_time = 0  # To track the last push-up time
push_up_pause = 0.5  # Minimum time (in seconds) to pause before counting again (to avoid multiple counts at the bottom)

# Timer variables
WORKOUT_DURATION = 60  # 60 seconds timer
start_time = time.time()
workout_active = True

# File to store click count
CLICKS_FILE = "clicks_remaining.txt"

# Initialize the file with 0 clicks or read existing value
try:
    with open(CLICKS_FILE, "r") as f:
        existing_clicks = int(f.read().strip())
except (FileNotFoundError, ValueError):
    existing_clicks = 0

with open(CLICKS_FILE, "w") as f:
    f.write(str(existing_clicks))

def calculate_angle(a, b, c):
    """Calculate the angle between three points"""
    angle = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    )
    if angle < 0:
        angle += 360
    return angle

def update_clicks_file(count):
    """Update the clicks file with the current count"""
    with open(CLICKS_FILE, "w") as f:
        f.write(str(count))

def get_random_comment(push_ups, workout_duration):
    global last_comment_type
    
    # List of available comment types
    comment_types = ['form', 'motivation', 'counting', 'tired']
    # Remove the last used type to avoid repetition
    if last_comment_type in comment_types:
        comment_types.remove(last_comment_type)
    
    # Choose a random comment type
    comment_type = random.choice(comment_types)
    last_comment_type = comment_type
    
    if comment_type == 'form':
        return random.choice(FORM_COMMENTS)
    elif comment_type == 'motivation':
        return random.choice(MOTIVATION_COMMENTS)
    elif comment_type == 'counting':
        return random.choice(COUNTING_COMMENTS).format(count=push_ups)
    else:  # tired
        return random.choice(TIRED_COMMENTS).format(duration=int(workout_duration))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame for a more intuitive mirror view
    frame = cv2.flip(frame, 1)

    # Calculate time remaining
    elapsed_time = time.time() - start_time
    time_remaining = max(0, WORKOUT_DURATION - elapsed_time)
    
    # Check if workout time is over
    if time_remaining <= 0 and workout_active:
        workout_active = False
        # Add pushups to existing clicks when time is up
        total_clicks = existing_clicks + push_ups
        update_clicks_file(total_clicks)
        print(f"Workout complete! You did {push_ups} push-ups. Total clicks: {total_clicks}")

    # Convert frame to RGB (MediaPipe needs RGB)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    # Check if pose landmarks are detected and workout is active
    if results.pose_landmarks and workout_active:
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
                    
                    # Add passive-aggressive feedback
                    current_time = time.time()
                    if current_time - last_comment_time >= comment_cooldown:
                        comment = get_random_comment(push_ups, current_time - start_time)
                        speak_text(comment)  # Use the non-blocking speak function
                        last_comment_time = current_time
                    
                is_pushing_up = True
        elif angle < 90:  # Arm bent (Bottom position)
            if is_pushing_up:
                # Add comment if they're not going low enough
                if angle > 70:  # Not going low enough
                    current_time = time.time()
                    if current_time - last_comment_time >= comment_cooldown:
                        speak_text("Lower! The floor won't bite, I promise.")
                        last_comment_time = current_time
                is_pushing_up = False

    # Display the current push-up count
    cv2.putText(frame, f'Push-ups: {push_ups}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    
    # Display time remaining and status
    if workout_active:
        cv2.putText(frame, f'Time remaining: {int(time_remaining)}s', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        total_expected = existing_clicks + push_ups
        cv2.putText(frame, f'Clicks to earn: {total_expected}', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    else:
        cv2.putText(frame, 'WORKOUT COMPLETE!', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, f'Total clicks available: {existing_clicks + push_ups}', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Render the landmarks on the image
    if results.pose_landmarks:
        mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Show the frame
    cv2.imshow("Push-Up Counter", frame)

    # Exit if the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Ensure the final count is saved
if workout_active:
    total_clicks = existing_clicks + push_ups
    update_clicks_file(total_clicks)
    print(f"Workout stopped early! Total clicks: {total_clicks}")

# Release resources
cap.release()
cv2.destroyAllWindows()
