def handle_type(goal_l):

    if not goal_l.startswith("type "):
        return None

    # Preserve original casing by slicing original goal later if needed
    text = goal_l.replace("type ", "", 1)

    if not text.strip():
        return None

    return {
        "action": "execute_plan",
        "plan": [
            {
                "action": "type",
                "text": text
            }
        ]
    }
