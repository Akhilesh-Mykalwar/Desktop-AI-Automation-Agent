def handle_universal_click(goal_l):

    if not goal_l.startswith("click"):
        return None

    # avoid youtube-specific reflex
    if "video" in goal_l:
        return None

    # click center
    if "center" in goal_l:
        return {
            "action": "execute_plan",
            "plan": [
                {"action": "click_position", "x": "center", "y": "center"}
            ]
        }

    # click top right
    if "top right" in goal_l:
        return {
            "action": "execute_plan",
            "plan": [
                {"action": "click_position", "x": "right", "y": "top"}
            ]
        }

    # click specific text
    if "click " in goal_l:
        value = goal_l.replace("click", "", 1).strip()

        return {
            "action": "execute_plan",
            "plan": [
                {
                    "action": "click_text_universal",
                    "text": value
                }
            ]
        }

    return None