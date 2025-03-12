import speech_recognition as sr
import pyttsx3
import time
import datetime
import os
import pywhatkit
import wikipedia
import webbrowser
import subprocess
import pyjokes
import random
import requests
import json
import psutil
import socket
import pyautogui
import cv2
import numpy as np
from email.message import EmailMessage
import smtplib
import weather_api


class EnhancedVoiceAssistant:
    def __init__(self, wake_word="Wake Up Prime"):
        # Store wake word first
        self.wake_word = wake_word.lower()
        
        # Initialize recognizer with optimized settings
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 2000
        self.recognizer.pause_threshold = 0.3
        self.recognizer.phrase_threshold = 0.1
        self.recognizer.non_speaking_duration = 0.2

        # Initialize text-to-speech
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)
        self.engine.setProperty('rate', 200)
        self.engine.setProperty('volume', 1.0)

        # State variables
        self.is_running = True
        self.is_active = False
        self.last_activity = time.time()
        self.activity_timeout = 180
        self.conversation_history = []
        self.reminder_list = []

        # Custom jokes collection
        self.jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why did the programmer quit his job? Because he didn't get arrays!",
            "What do you call a programmer from Finland? Nerdic!",
            "Why do Java developers wear glasses? Because they don't C#!",
            "What's a programmer's favorite hangout spot? The Foo Bar!"
        ]
        
        # About Prime Ai
        self.about="""
        I Am Prime AI
        Am Created For Helping Users Various Tasks
        users life is very easy were we working on..
        My Creator Used Many Advance Programms to create Me.."""
           
        # Configuration
        self.config = {
            'weather_api_key': 'YOUR_API_KEY',  # Get from OpenWeatherMap
            'email': 'your_email@gmail.com',
            'email_password': 'your_app_password',  # Gmail App Password
            'default_locations': {
                'home': 'your home address',
                'work': 'your work address'
            }
        }

    def speak(self, text):
        """Convert text to speech"""
        print(f"PRIME AI: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen_for_command(self, source, timeout=5):
        """Listen for user command"""
        try:
            print("Listening..." if not self.is_active else "Active...")
            
            audio = self.recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=5
            )
            
            command = self.recognizer.recognize_google(audio).lower()
            print(f"Heard: {command}")
            return command

        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            return None

    def get_random_joke(self):
        """Returns either a programming joke from pyjokes or a custom joke"""
        if random.choice([True, False]):
            try:
                return pyjokes.get_joke()
            except:
                return random.choice(self.jokes)
        return random.choice(self.jokes)

    def take_screenshot(self):
        """Capture and save screenshot"""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        screenshot = pyautogui.screenshot()
        filename = f"screenshot_{timestamp}.png"
        screenshot.save(filename)
        return filename

    def get_weather(self, city):
        """Get weather information"""
        try:
            api_key = self.config['weather_api_key']
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url)
            data = response.json()
            return f"Current temperature in {city} is {data['main']['temp']}°C with {data['weather'][0]['description']}"
        except Exception as e:
            return f"Error getting weather information: {str(e)}"

    def send_email(self, recipient, subject, content):
        """Send email using configured email account"""
        try:
            msg = EmailMessage()
            msg.set_content(content)
            msg['Subject'] = subject
            msg['From'] = self.config['email']
            msg['To'] = recipient
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(self.config['email'], self.config['email_password'])
                smtp.send_message(msg)
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False

    def take_webcam_photo(self):
        """Capture photo using webcam"""
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"webcam_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            cap.release()
            return filename
        cap.release()
        return None

    def get_system_stats(self):
        """Get system statistics"""
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return f"CPU Usage: {cpu_usage}%, Memory Usage: {memory.percent}%, Disk Usage: {disk.percent}%"

    def set_reminder(self, task, time_str):
        """Set a reminder"""
        try:
            reminder_time = datetime.datetime.strptime(time_str, "%H:%M")
            self.reminder_list.append({
                'task': task,
                'time': reminder_time,
                'completed': False
            })
            return True
        except Exception as e:
            print(f"Reminder error: {e}")
            return False

    def check_reminders(self):
        """Check for due reminders"""
        current_time = datetime.datetime.now()
        for reminder in self.reminder_list:
            if not reminder['completed'] and current_time.time() >= reminder['time'].time():
                self.speak(f"Reminder: {reminder['task']}")
                reminder['completed'] = True

    def execute_command(self, command):
        """Execute various commands"""
        if not command:
            return True

        self.last_activity = time.time()
        self.conversation_history.append(('user', command))

        try:
            # System Commands
            if "system stats" in command:
                stats = self.get_system_stats()
                self.speak(stats)

            # Screenshot Commands
            elif "screenshot" in command:
                filename = self.take_screenshot()
                self.speak(f"Screenshot saved as {filename}")

            # Weather Commands
            elif "weather" in command:
                city = command.split("weather in ")[-1] if "weather in " in command else "London"
                weather_info = self.get_weather(city)
                self.speak(weather_info)

            # Email Commands
            elif "send email" in command:
                self.speak("What's the recipient's email?")
                recipient = self.listen_for_command(timeout=10)
                self.speak("What's the subject?")
                subject = self.listen_for_command(timeout=10)
                self.speak("What's the message?")
                content = self.listen_for_command(timeout=15)
                
                if self.send_email(recipient, subject, content):
                    self.speak("Email sent successfully")
                else:
                    self.speak("Failed to send email")

            # Reminder Commands
            elif "set reminder" in command:
                self.speak("What should I remind you about?")
                task = self.listen_for_command(timeout=10)
                self.speak("At what time? (HH:MM format)")
                time_str = self.listen_for_command(timeout=10)
                
                if self.set_reminder(task, time_str):
                    self.speak("Reminder set successfully")
                else:
                    self.speak("Failed to set reminder")

            # Webcam Commands
            elif "take photo" in command:
                filename = self.take_webcam_photo()
                if filename:
                    self.speak(f"Photo saved as {filename}")
                else:
                    self.speak("Failed to take photo")

            # Time Commands
            elif "time" in command:
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                self.speak(f"The current time is {current_time}")

            # Date Commands
            elif "date" in command:
                current_date = datetime.datetime.now().strftime("%B %d, %Y")
                self.speak(f"Today is {current_date}")

            # Browser Commands
            elif "chrome" in command:
                subprocess.Popen(["C:\Program Files\Google\Chrome\Application\chrome.exe"])
                self.speak("Opening Chrome")

            elif "youtube" in command:
                webbrowser.open('https://youtube.com')
                self.speak("Opening Youtube")
                
            # About Me 
            elif any(word in command for word in ["who are you", "Prime ai", "About you"]):
                self.speak(self.about)

            # Play Commands
            elif "play" in command:
                song = command.replace('play', '')
                self.speak(f"Playing {song}")
                pywhatkit.playonyt(song)

            # Wikipedia Commands
            elif "who is" in command:
                person = command.replace('who is', '')
                info = wikipedia.summary(person, 4)
                self.speak(info)

            # Joke Commands
            elif any(word in command for word in ["tell me a joke", "joke", "make me laugh"]):
                joke = self.get_random_joke()
                self.speak(joke)

            # Sleep Mode
            elif "sleep" in command:
                self.is_active = False
                self.speak("Going to sleep. Wake me up when you need me!")

            # Exit Commands
            elif any(word in command for word in ["goodbye", "exit", "quit", "bye"]):
                self.speak("Goodbye! Thankyou For Your Interaction")
                self.is_running = False
                return False

            else:
                self.speak("I heard you, but I'm not sure how to help with that")

            self.check_reminders()
            return True

        except Exception as e:
            print(f"Error executing command: {e}")
            self.speak("Sorry, there was an error executing that command")
            return True

    def run(self):
        """Main method to run the assistant"""
        with sr.Microphone() as source:
            print("Adjusting for noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.speak("Say Wake Up Word to Assist!")

            while self.is_running:
                try:
                    if not self.is_active:
                        command = self.listen_for_command(source)
                        if command and self.wake_word in command:
                            self.is_active = True
                            self.last_activity = time.time()
                            self.speak("Activated!")
                            self.speak("How I Can Assist You")
                    else:
                        command = self.listen_for_command(source)
                        if command:
                            if not self.execute_command(command):
                                break
                            
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    continue

def main():
    assistant = EnhancedVoiceAssistant(wake_word="Wake Up Prime")
    assistant.run()

if __name__ == "__main__":
    main()