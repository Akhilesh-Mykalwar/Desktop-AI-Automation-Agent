def handle_double_click(goal_l):

    if not goal_l.startswith("double click"):
        return None

    # double click center
    if "center" in goal_l:
        return {
            "action": "execute_plan",
            "plan": [
                {"action": "double_click_position", "x": "center", "y": "center"}
            ]
        }

    # double click top right
    if "top right" in goal_l:
        return {
            "action": "execute_plan",
            "plan": [
                {"action": "double_click_position", "x": "right", "y": "top"}
            ]
        }

    # double click specific text
    value = goal_l.replace("double click", "", 1).strip()

    return {
        "action": "execute_plan",
        "plan": [
            {
                "action": "double_click_text",
                "text": value
            }
        ]
    }