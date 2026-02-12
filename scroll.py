import pyautogui
import time

def universal_scroll(direction="down", amount=800, smooth=True):
    
    # Ensure cursor is not over sidebar
    pyautogui.moveTo(800, 500)

    if not smooth:
        if direction == "down":
            pyautogui.scroll(-amount)
        else:
            pyautogui.scroll(amount)
        return

    # Smooth scroll
    step = 40
    delay = 0.02
    scrolled = 0

    while scrolled < amount:
        if direction == "down":
            pyautogui.scroll(-step)
        else:
            pyautogui.scroll(step)

        scrolled += step
        time.sleep(delay)