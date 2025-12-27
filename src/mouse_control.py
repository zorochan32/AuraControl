# mouse_control.py (Professional Gaming Edition)

import pydirectinput
import time

class MouseController:
    def __init__(self):
        pydirectinput.PAUSE = 0.005 # A small pause for stability
        self.screen_width, self.screen_height = pydirectinput.size()

    def move(self, dx, dy):
        """Moves the mouse relatively using DirectInput."""
        pydirectinput.moveRel(dx, dy, relative=True)

    def mouseDown(self, button='left'):
        """Presses and holds the specified mouse button."""
        pydirectinput.mouseDown(button=button)

    def mouseUp(self, button='left'):
        """Releases the specified mouse button."""
        pydirectinput.mouseUp(button=button)

    def keyDown(self, key):
        """Presses and holds the specified keyboard key."""
        pydirectinput.keyDown(key)

    def keyUp(self, key):
        """Releases the specified keyboard key."""
        pydirectinput.keyUp(key)

    # We keep these for single, quick actions if needed
    def click(self, button='left'):
        pydirectinput.click(button=button)

    def press(self, key):
        pydirectinput.press(key)

    def scroll(self, amount):
        pydirectinput.scroll(amount)

