def handle_scroll(goal_l):

    if not goal_l.startswith("scroll"):
        return None

    direction = "down"
    amount = 1500

    if "up" in goal_l:
        direction = "up"

    if any(w in goal_l for w in ["bit", "slight", "little"]):
        amount = 800
    elif any(w in goal_l for w in ["lot", "more", "much"]):
        amount = 2200

    return {
        "action": "execute_plan",
        "plan": [
            {
                "action": "scroll",
                "direction": direction,
                "amount": amount
            }
        ]
    }