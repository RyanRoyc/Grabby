# AI Fitness Gamification System
The annoying, janky, useless, and dumb project we made for Scrapyard Hacks Toronto, placing 4th against over 60 competitors! 

Project --> A unique fitness gamification system that combines push-up tracking, voice control, and robotic interaction. The system rewards users with "clicks" for completing push-ups, which can then be used to control the computer through voice commands or hand gestures.

## Features

### Push-up Counter
- Real-time push-up detection using computer vision
- Sarcastic AI commentary during workouts
- 60-second workout sessions
- Automatic click rewards for completed push-ups

### Voice-Controlled Clicking
- Voice command recognition for mouse clicks
- Click counter system with saved progress
- Text-to-speech feedback

### Hand Gesture Control
- Real-time hand tracking
- Smooth cursor movement using hand gestures
- Visual feedback with customizable crosshair

### Robotic Pointer Integration
- Arduino-based servo control system
- Physical pointer that follows cursor movement (shines a laser in your face while you drag the cursor)
- Smooth motion interpolation

## Requirements

### Software Dependencies
```python
opencv-python>=4.8.0
mediapipe>=0.10.0
pyautogui>=0.9.54
numpy>=1.24.0
SpeechRecognition>=3.10.0
pyttsx3>=2.90
pyaudio>=0.2.11

# Windows-only dependencies:
keyboard>=0.13.5
pywin32>=305
```

### Hardware Requirements
- Webcam
- Microphone
- Arduino board
- 2 servo motors
- USB cable for Arduino connection

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Upload the Arduino sketch:
   - Open `shitty_robot/shitty_robot.ino` in Arduino IDE
   - Upload to your Arduino board
   - Note the COM port being used

4. Update the serial port in `mouse_controller.py`:
   ```python
   ser = serial.Serial('/dev/cu.usbmodem11201', 9600)  # Update with your port
   ```

## Usage

### Push-up Counter
```bash
python push_up_counter.py
```
Stand in view of the webcam, perform push-ups within the 60-second time limit. Earned clicks will be automatically saved.

### Voice Clicker
```bash
python voice_clicker.py
```
Use voice commands to trigger clicks. Monitor remaining clicks in the terminal.

### Hand Gesture Control
```bash
python mouse_controller.py
```
Use hand gestures to control the cursor. Close fingers to grab and move. The robotic pointer will follow cursor movement.

## Project Structure
- `push_up_counter.py`: Main workout tracking system
- `voice_clicker.py`: Voice command interface
- `mouse_controller.py`: Hand gesture tracking and cursor control
- `shitty_robot/shitty_robot.ino`: Arduino servo control code

## Troubleshooting

### Serial Port Issues
- Verify the correct port in Arduino IDE
- Update the port in `mouse_controller.py`
- Ensure proper USB connection

### Webcam Access
- Check webcam permissions
- Verify correct webcam index (default: 0)

### Voice Recognition
- Ensure microphone access
- Check audio input levels
- Install required audio drivers

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

We do not care...
