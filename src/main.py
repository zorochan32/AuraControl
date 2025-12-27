import cv2
import time
import keyboard

from hand_tracking import HandTracker
from mouse_control import MouseController
from voice_control import VoiceController
from config import ENABLE_VOICE


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera not found")
        return

    hand_tracker = HandTracker()
    mouse = MouseController()

    # وضعیت‌ها
    walking = False

    # Voice callback
    def on_voice_command(cmd):
        nonlocal walking
        if cmd == "open":
            keyboard.press('e')
            keyboard.release('e')
            print("Inventory opened")
        elif cmd == "close":
            keyboard.press('esc')
            keyboard.release('esc')
            print("Inventory closed")

    # Voice system
    voice = VoiceController(enabled=ENABLE_VOICE)
    voice.start(on_voice_command)

    print("System started. Press ESC to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        left, right = hand_tracker.process_frame(frame)

        # --------- LEFT HAND (movement) ----------
        if left:
            fingers = hand_tracker.fingers_status(left)

            # حرکت جلو
            if fingers == [1, 1, 1, 1, 1]:
                if not walking:
                    keyboard.press('w')
                    walking = True
            else:
                if walking:
                    keyboard.release('w')
                    walking = False

            # پرش
            if fingers == [0, 1, 0, 0, 0]:
                keyboard.press_and_release('space')

        else:
            if walking:
                keyboard.release('w')
                walking = False

        # --------- RIGHT HAND (mouse) ----------
        if right:
            dx, dy = hand_tracker.get_mouse_delta(right)
            mouse.move(dx, dy)

            fingers_r = hand_tracker.fingers_status(right)

            # کلیک چپ (دو انگشت)
            if fingers_r[1] and fingers_r[2]:
                mouse.left_click_hold(True)
            else:
                mouse.left_click_hold(False)

            # کلیک راست (فقط شست)
            if fingers_r == [1, 0, 0, 0, 0]:
                mouse.right_click()

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
