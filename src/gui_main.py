# gui_main.py (Final version with Mirror Mode selection)

import tkinter
import customtkinter
from PIL import Image, ImageTk
import cv2
import threading
import speech_recognition as sr
import time

from hand_tracking import HandTracker
from mouse_control import MouseController
from voice_control import VoiceController
from config import *

ACTION_COOLDOWN = 1.0

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("AuraControl")
        self.geometry("1200x700")
        customtkinter.set_appearance_mode("Dark")
        customtkinter.set_default_color_theme("blue")

        self.is_running = False
        
        # --- NEW: Mirror Mode variable, default is ON ---
        self.mirror_mode_enabled = customtkinter.BooleanVar(value=True)

        self.hand_tracking_enabled = customtkinter.BooleanVar(value=True)
        self.voice_control_enabled = customtkinter.BooleanVar(value=ENABLE_VOICE)
        self.mouse_control_enabled = customtkinter.BooleanVar(value=True)
        
        self.key_states = {
            'w': False, 'a': False, 's': False, 'd': False,
            'ctrl': False, 'space': False, 'e': False,
            'left_mouse': False, 'right_mouse': False
        }
        self.last_momentary_action_time = 0

        self.cap = None
        self.hand_tracker = HandTracker()
        self.mouse = MouseController()
        self.voice_controller = VoiceController(enabled=self.voice_control_enabled.get())
        self.voice_thread = None
        
        self.camera_list = self.get_available_cameras()
        self.mic_list = self.get_available_microphones()
        self.selected_camera = customtkinter.StringVar(value=self.camera_list[0] if self.camera_list else "No Cameras Found")
        self.selected_mic = customtkinter.StringVar(value=self.mic_list[0] if self.mic_list else "No Microphones Found")

        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(0, weight=1)
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=10); self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=3); self.main_frame.grid_columnconfigure(1, weight=1); self.main_frame.grid_rowconfigure(0, weight=1)
        self.video_label = customtkinter.CTkLabel(self.main_frame, text="Click 'Start' to begin", font=customtkinter.CTkFont(size=20)); self.video_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.controls_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=10); self.controls_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        
        self.device_label = customtkinter.CTkLabel(self.controls_frame, text="Device Selection", font=customtkinter.CTkFont(size=16, weight="bold")); self.device_label.pack(pady=(15, 10))
        self.camera_menu = customtkinter.CTkOptionMenu(self.controls_frame, values=self.camera_list, variable=self.selected_camera); self.camera_menu.pack(pady=5, padx=20, fill="x")
        self.mic_menu = customtkinter.CTkOptionMenu(self.controls_frame, values=self.mic_list, variable=self.selected_mic); self.mic_menu.pack(pady=5, padx=20, fill="x")
        
        self.controls_label = customtkinter.CTkLabel(self.controls_frame, text="Controls", font=customtkinter.CTkFont(size=16, weight="bold")); self.controls_label.pack(pady=(20, 10))
        self.start_stop_button = customtkinter.CTkButton(self.controls_frame, text="Start", command=self.toggle_start_stop, height=40); self.start_stop_button.pack(pady=10, padx=20, fill="x")

        # --- NEW: Mirror Mode Switch ---
        self.mirror_switch = customtkinter.CTkSwitch(self.controls_frame, text="Mirror Camera View", variable=self.mirror_mode_enabled, font=customtkinter.CTkFont(size=14))
        self.mirror_switch.pack(pady=10, padx=20, fill="x")

        self.hand_switch = customtkinter.CTkSwitch(self.controls_frame, text="Hand Tracking", variable=self.hand_tracking_enabled, font=customtkinter.CTkFont(size=14)); self.hand_switch.pack(pady=10, padx=20, fill="x")
        self.mouse_switch = customtkinter.CTkSwitch(self.controls_frame, text="Mouse Control", variable=self.mouse_control_enabled, font=customtkinter.CTkFont(size=14)); self.mouse_switch.pack(pady=10, padx=20, fill="x")
        self.voice_switch = customtkinter.CTkSwitch(self.controls_frame, text="Voice Control", variable=self.voice_control_enabled, command=self.toggle_voice_control, font=customtkinter.CTkFont(size=14)); self.voice_switch.pack(pady=10, padx=20, fill="x")
        
        self.status_frame = customtkinter.CTkFrame(self.controls_frame, corner_radius=10); self.status_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.status_title_label = customtkinter.CTkLabel(self.status_frame, text="Status", font=customtkinter.CTkFont(size=16, weight="bold")); self.status_title_label.pack(pady=(10, 5))
        self.status_label = customtkinter.CTkLabel(self.status_frame, text="Idle", font=customtkinter.CTkFont(size=14), wraplength=220, justify="center"); self.status_label.pack(pady=5, padx=5, fill="both", expand=True)

    def get_available_cameras(self):
        cam_list_dshow = [f"Camera {i}" for i in range(10) if cv2.VideoCapture(i, cv2.CAP_DSHOW).isOpened()]
        if cam_list_dshow: return cam_list_dshow
        cam_list_default = [f"Camera {i}" for i in range(10) if cv2.VideoCapture(i).isOpened()]
        return cam_list_default if cam_list_default else ["No Cameras Found"]

    def start(self):
        if "No Cameras" in self.selected_camera.get(): return
        self.is_running = True
        self.camera_menu.configure(state="disabled"); self.mic_menu.configure(state="disabled")
        self.mirror_switch.configure(state="disabled") # Disable while running
        self.start_stop_button.configure(text="Stop", fg_color="#db524b")
        cam_index = int(self.selected_camera.get().split()[-1])
        self.cap = cv2.VideoCapture(cam_index)
        if not self.cap.isOpened(): self.stop(); return
        if self.voice_control_enabled.get(): self.start_voice_thread()
        self.update_frame()

    def stop(self):
        self.is_running = False
        self.release_all_keys()
        self.camera_menu.configure(state="normal"); self.mic_menu.configure(state="normal")
        self.mirror_switch.configure(state="normal") # Re-enable when stopped
        self.start_stop_button.configure(text="Start", fg_color=("#3b8ed0", "#1f6aa5"))
        if self.cap: self.cap.release()
        self.video_label.configure(image=None, text="Click 'Start' to begin"); self.status_label.configure(text="Idle")
        if self.voice_thread and self.voice_thread.is_alive(): self.voice_controller.stop()

    def release_all_keys(self):
        print("Releasing all held keys...")
        for key, is_down in self.key_states.items():
            if is_down:
                if 'mouse' in key: self.mouse.mouseUp(button=key.split('_')[0])
                else: self.mouse.keyUp(key)
                self.key_states[key] = False

    def update_frame(self):
        if not self.is_running: return
        ret, frame = self.cap.read()
        if not ret: self.stop(); return

        # --- NEW: Conditional Mirroring ---
        if self.mirror_mode_enabled.get():
            frame = cv2.flip(frame, 1)
        
        desired_key_states = {k: False for k in self.key_states}
        active_actions = []
        
        if self.hand_tracking_enabled.get():
            left_hand, right_hand = self.hand_tracker.process_frame(frame.copy())

            # --- NEW: Critical Logic Swap for Un-mirrored View ---
            if not self.mirror_mode_enabled.get():
                # In a non-mirrored view, the user's right hand appears on the left.
                # To keep controls intuitive, we swap the detected hands.
                left_hand, right_hand = right_hand, left_hand

            if self.mouse_control_enabled.get():
                # Right Hand Logic...
                if right_hand:
                    dx, dy = self.hand_tracker.get_camera_rotation_delta(right_hand)
                    self.mouse.move(dx, dy)
                    active_actions.append("Camera")
                    status_r = self.hand_tracker.fingers_status(right_hand)
                    can_press = (time.time() - self.last_momentary_action_time) > ACTION_COOLDOWN
                    if can_press and status_r == [1, 0, 0, 0, 0]:
                        self.mouse.press('space')
                        active_actions.append("Jump!")
                        self.last_momentary_action_time = time.time()
                    else:
                        if sum(status_r) == 5: desired_key_states['w'] = True; active_actions.append("Forward")
                        elif self.hand_tracker.is_thumb_pointing_left(right_hand): desired_key_states['a'] = True; active_actions.append("Strafe Left")
                        elif self.hand_tracker.is_thumb_pointing_right(right_hand): desired_key_states['d'] = True; active_actions.append("Strafe Right")
                        elif self.hand_tracker.is_thumb_down(right_hand) and sum(status_r[1:]) == 0: desired_key_states['ctrl'] = True; active_actions.append("Crouch")
                # Left Hand Logic...
                if left_hand:
                    status_l = self.hand_tracker.fingers_status(left_hand)
                    can_press = (time.time() - self.last_momentary_action_time) > ACTION_COOLDOWN
                    if can_press and status_l == [0, 1, 1, 0, 0]:
                        self.mouse.press('e')
                        active_actions.append("Inventory!")
                        self.last_momentary_action_time = time.time()
                    else:
                        if sum(status_l) == 0: desired_key_states['left_mouse'] = True; active_actions.append("LMB Hold")
                        elif status_l == [0, 1, 0, 0, 0]: desired_key_states['right_mouse'] = True; active_actions.append("RMB Hold")

        # Apply state changes... (unchanged)
        for key, should_be_down in desired_key_states.items():
            if should_be_down and not self.key_states[key]:
                if 'mouse' in key: self.mouse.mouseDown(button=key.split('_')[0])
                else: self.mouse.keyDown(key)
                self.key_states[key] = True
            elif not should_be_down and self.key_states[key]:
                if 'mouse' in key: self.mouse.mouseUp(button=key.split('_')[0])
                else: self.mouse.keyUp(key)
                self.key_states[key] = False
        
        self.status_label.configure(text=', '.join(active_actions) if active_actions else "Idle")

        # Display Logic... (unchanged)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame); ctk_img = customtkinter.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
        self.video_label.configure(image=ctk_img, text=""); self.video_label.image = ctk_img
        self.after(10, self.update_frame)

    def on_closing(self):
        self.stop(); self.destroy()
        
    def get_available_microphones(self):
        try: return sr.Microphone.list_microphone_names()
        except: return ["No Microphones Found"]
    def toggle_start_stop(self):
        if self.is_running: self.stop()
        else: self.start()
    def toggle_voice_control(self):
        is_enabled = self.voice_control_enabled.get()
        self.voice_controller.enabled = is_enabled
        if self.is_running:
            if is_enabled and (self.voice_thread is None or not self.voice_thread.is_alive()): self.start_voice_thread()
            elif not is_enabled and self.voice_thread and self.voice_thread.is_alive(): self.voice_controller.stop()
    def start_voice_thread(self):
        if "No Microphones Found" in self.mic_list[0]: return
        mic_name = self.selected_mic.get()
        mic_index = self.mic_list.index(mic_name)
        if self.voice_controller.initialize_audio(device_index=mic_index):
            self.voice_thread = threading.Thread(target=self.voice_controller.listen_in_background, daemon=True)
            self.voice_thread.start()

if __name__ == "__main__":
    app = App()
    app.mainloop()
