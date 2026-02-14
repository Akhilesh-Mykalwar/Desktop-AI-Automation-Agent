import subprocess
import time
import pyautogui

from vision_ocr import find_text_on_screen

# Safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


def open_url(url):
    """
    Open a URL in the default browser.
    Uses Windows 'start' to avoid focus issues.
    """
    subprocess.Popen(["cmd", "/c", "start", "", url])
    time.sleep(2)  # wait for browser to open and focus

def open_uwp(app_name):
    subprocess.Popen([
        "powershell",
        "-Command",
        f"start shell:AppsFolder\\{app_name}"
    ])
    time.sleep(2)


def open_app(cmd):
    subprocess.Popen(cmd)
    time.sleep(1)


def open_uri(uri):
    subprocess.Popen(["cmd", "/c", "start", "", uri])
    time.sleep(2)


def execute(action):
    """
    Execute a single action dictionary.
    """

    act = action.get("action")

    if act == "open_url":
        open_url(action["url"])

    elif act == "open_uri":
        open_uri(action["uri"])

    elif act == "scroll":

        direction = action.get("direction", "down")
        amount = action.get("amount", 1500)

        pyautogui.moveTo(800, 500)

        step = 40
        delay = 0.01
        scrolled = 0

        while scrolled < amount:
            if direction == "down":
                pyautogui.scroll(-step)
            else:
                pyautogui.scroll(step)

            scrolled += step
            time.sleep(delay)



    elif act == "volume_up":
        for _ in range(action.get("amount", 5)):
            pyautogui.press("volumeup")

    elif act == "volume_down":
        for _ in range(action.get("amount", 5)):
            pyautogui.press("volumedown")

    elif act == "mute":
        pyautogui.press("volumemute")

    elif act == "brightness_up":
        for _ in range(action.get("amount", 3)):
            pyautogui.press("brightnessup")

    elif act == "brightness_down":
        for _ in range(action.get("amount", 3)):
            pyautogui.press("brightnessdown")
        



    elif act == "click_text_universal":

        from vision_ocr import find_text_on_screen

        text = action.get("text")

        coords = find_text_on_screen(text)

        if coords:
            pyautogui.click(coords[0], coords[1])
        else:
            print("❌ Text not found:", text)


    elif act == "double_click_text":

        from vision_ocr import find_text_on_screen

        text = action.get("text")

        coords = find_text_on_screen(text)

        if coords:
            pyautogui.doubleClick(coords[0], coords[1])
        else:
            print("❌ Text not found:", text)

            

    elif act == "type":
        pyautogui.write(action["text"], interval=0.05)

    elif act == "press":
        pyautogui.press(action["key"])

    elif act == "hotkey":
        # expects: {"action": "hotkey", "keys": ["ctrl", "l"]}
        pyautogui.hotkey(*action["keys"])

    elif act == "wait":
        time.sleep(action.get("time", 1))
    
    elif act == "open_app":
        open_app(action["cmd"])
    elif act == "click_text":
        coords = find_text_on_screen(action["text"])
        if coords:
            pyautogui.click(coords[0], coords[1])
        else:
            print("❌ Text not found:", action["text"])

    elif act == "open_uwp":
        subprocess.Popen([
        "explorer.exe",
        f"shell:AppsFolder\\{action['name']}"
    ])


    elif act == "done":
        pass

    elif act == "click_video":

        from vision_ocr import (
            find_first_video_title,
            find_video_by_title,
            find_video_by_channel
        )

        mode = action.get("mode")
        value = action.get("value", "")

        time.sleep(1)  # allow screen to stabilize

        if mode == "first":
            result = find_first_video_title()

        elif mode == "title":
            result = find_video_by_title(value)

        elif mode == "channel":
            result = find_video_by_channel(value)

        else:
            result = None

        if result:
            pyautogui.click(result["center_x"], result["center_y"])
        else:
            print("❌ Video not found")
        
        
    else:
        raise ValueError(f"Unknown action: {action}")
