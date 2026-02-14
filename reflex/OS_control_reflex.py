import re
import subprocess



def extract_time_seconds(goal_l):
    """
    Extract time from goal and convert to seconds.
    Supports:
    - minutes
    - hours
    - seconds
    """

    match = re.search(r"(\d+)", goal_l)
    if not match:
        return None

    value = int(match.group(1))

    if "hour" in goal_l:
        return value * 3600
    if "minute" in goal_l:
        return value * 60
    if "second" in goal_l:
        return value

    return None



def extract_amount(goal_l, default=10):
    match = re.search(r"(\d+)", goal_l)
    if match:
        return int(match.group(1))
    return default


def handle_os_controls(goal_l):

    # ---------------- LOCK SCREEN ----------------
    if "lock screen" in goal_l or "lock pc" in goal_l:
        return {
            "action": "execute_plan",
            "plan": [
                {"action": "lock_screen"}
            ]
        }

    # ---------------- SLEEP ----------------
    if "sleep pc" in goal_l or "sleep computer" in goal_l:
        return {
            "action": "execute_plan",
            "plan": [
                {"action": "sleep_pc"}
            ]
        }

    # ---------------- SHUTDOWN ----------------
    if "shutdown" in goal_l:
        return {
            "action": "execute_plan",
            "plan": [
                {"action": "shutdown_pc"}
            ]
        }


        # ---------------- TIMED SHUTDOWN ----------------
    if "shutdown" in goal_l and ("in" in goal_l or "after" in goal_l):

        seconds = extract_time_seconds(goal_l)

        if seconds:
            return {
                "action": "execute_plan",
                "plan": [
                    {
                        "action": "shutdown_timer",
                        "seconds": seconds
                    }
                ]
            }

    # ---------------- CANCEL SHUTDOWN ----------------
    if "cancel shutdown" in goal_l:
        return {
            "action": "execute_plan",
            "plan": [
                {"action": "cancel_shutdown"}
            ]
        }






    # ---------------- VOLUME ----------------
    if "volume" in goal_l:
        amount = extract_amount(goal_l, default=10)
        steps = max(1, int(amount / 2))

        if "up" in goal_l or "increase" in goal_l:
            return {
                "action": "execute_plan",
                "plan": [
                    {"action": "volume_up", "amount": steps}
                ]
            }

        if "down" in goal_l or "decrease" in goal_l:
            return {
                "action": "execute_plan",
                "plan": [
                    {"action": "volume_down", "amount": steps}
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

        amount = extract_amount(goal_l, default=10)

        if "up" in goal_l or "increase" in goal_l:
            return {
                "action": "execute_plan",
                "plan": [
                    {
                        "action": "set_brightness_relative",
                        "direction": "up",
                        "amount": amount
                    }
                ]
            }

        if "down" in goal_l or "decrease" in goal_l:
            return {
                "action": "execute_plan",
                "plan": [
                    {
                        "action": "set_brightness_relative",
                        "direction": "down",
                        "amount": amount
                    }
                ]
            }



    return None
