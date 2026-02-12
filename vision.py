from PIL import ImageGrab
from config import SCREENSHOT_PATH

def capture_screen():
    img = ImageGrab.grab()
    img.save(SCREENSHOT_PATH)
    return SCREENSHOT_PATH
