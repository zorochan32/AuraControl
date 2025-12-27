# voice_control.py (Updated for device selection)

import speech_recognition as sr
import threading
import time

class VoiceController:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self._stop_event = threading.Event()
        self.last_command = None
        self.recognizer = None
        self.microphone = None
        self.device_index = None # برای نگهداری ایندکس میکروفون

    def initialize_audio(self, device_index=None):
        """Initializes audio components with a specific device."""
        self.device_index = device_index
        try:
            self.recognizer = sr.Recognizer()
            # Use the specified microphone index
            self.microphone = sr.Microphone(device_index=self.device_index)
            with self.microphone as source:
                print("Adjusting for ambient noise, please be quiet...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Ready to hear voice commands.")
            return True
        except Exception as e:
            print(f"Error initializing audio device: {e}")
            self.enabled = False
            return False

    def listen_in_background(self):
        """This method runs in a separate thread to avoid freezing the GUI."""
        self._stop_event.clear()
        while not self._stop_event.is_set():
            if not self.enabled or not self.recognizer:
                time.sleep(0.5)
                continue

            command = self._listen_once()
            if command:
                self.last_command = command

    def _listen_once(self):
        """Tries to capture a single voice command."""
        if not self.microphone or not self.recognizer:
            return None
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=4)
            command = self.recognizer.recognize_google(audio, language="en-US").lower()
            print(f"Command identified: {command}")
            return command
        except sr.WaitTimeoutError:
            return None # Silence
        except sr.UnknownValueError:
            return None # Unintelligible speech
        except sr.RequestError as e:
            print(f"API Error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in voice recognition: {e}")
            return None

    def get_last_command(self):
        """Returns the last command and clears it."""
        cmd = self.last_command
        self.last_command = None
        return cmd

    def stop(self):
        """Signals the background thread to stop."""
        print("Stopping voice listener...")
        self._stop_event.set()

    def start(self):
        """Re-initializes audio if needed."""
        if self.enabled and not self.recognizer:
            self.initialize_audio(self.device_index)
        self._stop_event.clear()
