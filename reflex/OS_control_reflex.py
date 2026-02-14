import pyautogui

def handle_os_controls(goal_l):

    if "volume" in goal_l:
        amount = 5

        if "up" in goal_l or "increase" in goal_l:
            return {
                "action": "execute_plan",
                "plan": [
                    {"action": "volume_up", "amount": amount}
                ]
            }

        if "down" in goal_l or "decrease" in goal_l:
            return {
                "action": "execute_plan",
                "plan": [
                    {"action": "volume_down", "amount": amount}
                ]
            }

        if "mute" in goal_l:
            return {
                "action": "execute_plan",
                "plan": [
                    {"action": "mute"}
                ]
            }

    if "brightness" in goal_l:
        if "up" in goal_l or "increase" in goal_l:
            return {
                "action": "execute_plan",
                "plan": [
                    {"action": "brightness_up"}
                ]
            }

        if "down" in goal_l or "decrease" in goal_l:
            return {
                "action": "execute_plan",
                "plan": [
                    {"action": "brightness_down"}
                ]
            }

    return None
