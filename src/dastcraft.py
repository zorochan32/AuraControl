import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import keyboard
import pygetwindow as gw
import win32gui
import win32con
import win32api
import time
import math
from collections import deque
import speech_recognition as sr
import threading
import difflib

# ================== تنظیمات اولیه ==================
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# کمی تاخیر برای آماده‌سازی
time.sleep(1)

# فوکوس کردن پنجره‌ی Minecraft
for _ in range(3):
    try:
        win = gw.getWindowsWithTitle("Minecraft")[0]
        if win.isMinimized:
            win.restore()
        hwnd = win._hWnd
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        break
    except Exception:
        time.sleep(1)

# MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.6
)

# پارامترهای کنترل حرکت دست
w_pressed = False
last_space_time = 0

# حساسیت دوربین
CAM_SENS_X = 80
CAM_SENS_Y = 60
THRESH = 0.015

# صف‌های smoothing برای محورهای X/Y
SMOOTH_FACTOR = 5
dx_queue = deque(maxlen=SMOOTH_FACTOR)
dy_queue = deque(maxlen=SMOOTH_FACTOR)

# ================== توابع کمکی ==================


def distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def fingers_status(lm):
    tips = [4, 8, 12, 16, 20]
    out = [1 if lm[tips[0]].x < lm[tips[0] - 1].x else 0]
    for i in range(1, 5):
        out.append(1 if lm[tips[i]].y < lm[tips[i] - 2].y else 0)
    return out


def is_scissor(lm):
    return distance(lm[8], lm[12]) > 0.06


def move_mouse_raw(dx, dy):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)


# ================== Voice Control ==================
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.pause_threshold = 0.5
mic = sr.Microphone()
running = True

# معادل‌های صوتی
open_variants = ["open inventory", "inventory",
                 "open inv", "open inve", "opan inv"]
close_variants = ["close inventory", "close inv", "close inve"]


def similar(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def listen_for_commands():
    global running
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    while running:
        try:
            with mic as source:
                audio = recognizer.listen(source, phrase_time_limit=6)
            command = recognizer.recognize_google(audio).lower()
            print(f"Recognized command: {command}")

            # Open Inventory
            if any(v in command for v in open_variants) or similar(command, "open inventory") > 0.7:
                win = gw.getWindowsWithTitle("Minecraft")[0]
                win32gui.SetForegroundWindow(win._hWnd)
                pyautogui.press('e')
                print("🔓 Inventory opened")
            # Close Inventory
            elif any(v in command for v in close_variants) or similar(command, "close inventory") > 0.7:
                win = gw.getWindowsWithTitle("Minecraft")[0]
                win32gui.SetForegroundWindow(win._hWnd)
                pyautogui.press('esc')
                print("🔒 Inventory closed")

        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Speech service error: {e}")
            time.sleep(1)
        time.sleep(0.1)


# اجرای ترد Voice Control
t = threading.Thread(target=listen_for_commands, daemon=True)
t.start()

# ================== حلقه اصلی ==================
cap = cv2.VideoCapture(0)
time.sleep(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    left_lm = None
    right_lm = None
    if results.multi_hand_landmarks and results.multi_handedness:
        for lm_obj, handness in zip(results.multi_hand_landmarks, results.multi_handedness):
            if handness.classification[0].label == 'Left':
                left_lm = lm_obj.landmark
            else:
                right_lm = lm_obj.landmark

    # کنترل با دست چپ (کیبورد)
    if left_lm:
        f = fingers_status(left_lm)
        if f == [1, 1, 1, 1, 1] and not w_pressed:
            keyboard.press('w')
            w_pressed = True
        elif f == [0, 0, 0, 0, 0] and w_pressed:
            keyboard.release('w')
            w_pressed = False
        elif f == [0, 1, 0, 0, 0]:
            now = time.time()
            if now - last_space_time > 0.4:
                keyboard.send('space')
                last_space_time = now
    else:
        if w_pressed:
            keyboard.release('w')
            w_pressed = False

    # کنترل با دست راست (ماوس)
    if right_lm:
        dx = right_lm[9].x - 0.5
        dy = right_lm[9].y - 0.5
        dx_queue.append(dx)
        dy_queue.append(dy)
        dx_s = sum(dx_queue)/len(dx_queue)
        dy_s = sum(dy_queue)/len(dy_queue)
        if abs(dx_s) > THRESH:
            move_mouse_raw(int(dx_s*CAM_SENS_X), 0)
        if abs(dy_s) > THRESH:
            move_mouse_raw(0, int(dy_s*CAM_SENS_Y))

        f2 = fingers_status(right_lm)
        if f2[1] == 1 and f2[2] == 1 and is_scissor(right_lm):
            pyautogui.mouseDown(button='left')
        else:
            pyautogui.mouseUp(button='left')
        if f2 == [1, 0, 0, 0, 0]:
            pyautogui.click(button='right')
            time.sleep(0.2)
    else:
        pyautogui.mouseUp(button='left')

    if cv2.waitKey(1) & 0xFF == 27:
        running = False
        break

cap.release()
cv2.destroyAllWindows()
