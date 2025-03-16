<<<<<<< HEAD
# Hand Mouse Controller

This Python application enables hand gesture-based mouse control using your webcam. It tracks your hand movements and allows you to control the mouse cursor using natural hand gestures.

## Features

- Real-time hand tracking using MediaPipe
- Smooth cursor movement with moving average filter
- Mouse click/drag functionality based on hand gestures
- Easy program termination with 'q' key
- Low latency and optimized performance

## Requirements

- Python 3.7 or higher
- Webcam
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone this repository or download the files
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the script:
   ```bash
   python hand_mouse_controller.py
   ```

2. Position your hand in front of the webcam
3. Control the cursor:
   - Move your hand to control cursor position
   - Close your hand (make a fist) to click and drag
   - Open your hand to release the click
4. Press 'q' to quit the program

## Controls

- Hand Movement: Controls cursor position
- Closed Fist: Click and drag
- Open Hand: Release click
- 'q' Key: Quit program

## Notes

- The program uses the base of your index finger (MCP joint) for cursor tracking
- A moving average filter is implemented to reduce cursor jitter
- The trackpad/mouse remains active while the program runs
- Adjust your hand position and lighting for optimal tracking

## Troubleshooting

If the cursor movement is too sensitive or not responsive enough, you can adjust these parameters in the code:
- `SMOOTHING_BUFFER_SIZE`: Increase for smoother but slower movement
- `min_detection_confidence` and `min_tracking_confidence`: Adjust for better hand detection
- Finger distance threshold: Modify the `0.1` value in the `finger_distance` check for different click sensitivity 
=======
# Grabby
>>>>>>> 89b0c0091a27966e9b54264406fa8e0676def95b
