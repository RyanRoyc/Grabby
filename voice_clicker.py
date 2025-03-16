import speech_recognition as sr
import pyttsx3
import pyautogui
import os

# Initialize the recognizer and the speaker
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Function to speak to the user
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to read remaining clicks from file
def read_clicks():
    if not os.path.exists("clicks_remaining.txt"):
        with open("clicks_remaining.txt", "w") as file:
            file.write("10")  # Default value if file doesn't exist
    with open("clicks_remaining.txt", "r") as file:
        return int(file.readline().strip())

# Function to write remaining clicks to file
def write_clicks(remaining):
    with open("clicks_remaining.txt", "w") as file:
        file.write(str(remaining))

# Function to listen to the user's command
def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"User said: {command}")
        except sr.UnknownValueError:
            speak("Sorry, I could not understand what you said. Please try again.")
            return listen()
        except sr.RequestError:
            speak("Sorry, there seems to be a problem with the speech service.")
            return listen()
        return command.lower()

# Function to handle clicks and decrement counter
def click():
    remaining_clicks = read_clicks()
    if remaining_clicks > 0:
        speak("Clicking...")
        pyautogui.click()
        remaining_clicks -= 1
        write_clicks(remaining_clicks)
        print(f"Remaining clicks: {remaining_clicks}")
        if remaining_clicks == 0:
            speak("You have no clicks remaining.")
    else:
        speak("No clicks remaining. Please reset your clicks.")

# Function to execute user commands
def execute_command(command):
    if "press" in command or "mouse" in command or "button" in command or "click" in command:
        click()
    else:
        speak("Sorry, I did not understand that command.")

# Main loop to keep the assistant listening
def main():
    print("Listening for commands...")
    while True:
        command = listen()
        execute_command(command)

if __name__ == "__main__":
    main()
