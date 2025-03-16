import cv2
import numpy as np
import serial
import time

# Initialize webcam
cap = cv2.VideoCapture(0)

# Define the color range for tracking (e.g., a specific color the person is wearing)
# These values are for a specific color range in HSV color space
# Adjust these values based on your needs
lower_color = np.array([0, 50, 50])
upper_color = np.array([10, 255, 255])

# Set up serial communication
ser = serial.Serial('/dev/cu.usbmodem11201', 9600)  # Replace 'COM10' with your Arduino's port

# Allow time for the serial connection to initialize
time.sleep(2)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the color range
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Apply mask to frame
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Convert the result to grayscale for contour detection
    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

    # Find contours in the mask
    contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Get the largest contour
        largest_contour = max(contours, key=cv2.contourArea)

        # Get the bounding box for the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Calculate the center of the bounding box
        center_x = x + w // 2
        center_y = y + h // 2

        # Send the coordinates to Arduino
        ser.write(f"{center_x},{center_y}\n".encode())

        # Draw bounding box and center point
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

        # Print center coordinates
        print(f"Center coordinates: ({center_x}, {center_y})")

    # Show the resulting frame
    cv2.imshow('Tracking', frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
ser.close()
