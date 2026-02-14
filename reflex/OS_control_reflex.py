import re

def extract_amount(goal_l, default=10):
    match = re.search(r"(\d+)", goal_l)
    if match:
        return int(match.group(1))
    return default


def handle_os_controls(goal_l):

    # ---------------- VOLUME ----------------
    if "volume" in goal_l:

        amount = extract_amount(goal_l, default=10)

        # Convert percentage to key presses
        # Windows volume usually has ~50 steps
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

    # ---------------- BRIGHTNESS ----------------
    if "brightness" in goal_l:

        amount = extract_amount(goal_l, default=10)
        steps = max(1, int(amount / 5))

        if "up" in goal_l or "increase" in goal_l:
            return {
                "action": "execute_plan",
                "plan": [
                    {"action": "brightness_up", "amount": steps}
                ]
            }

        if "down" in goal_l or "decrease" in goal_l:
            return {
                "action": "execute_plan",
                "plan": [
                    {"action": "brightness_down", "amount": steps}
                ]
            }

    return None
