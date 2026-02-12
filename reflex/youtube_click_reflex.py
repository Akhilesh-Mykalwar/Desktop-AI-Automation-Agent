def handle_youtube_click(goal_l):

    if not goal_l.startswith("click") or "video" not in goal_l:
        return None

    if "first" in goal_l or "1st" in goal_l:
        return {
            "action": "execute_plan",
            "plan": [
                {
                    "action": "click_video",
                    "mode": "first"
                }
            ]
        }

    if "by" in goal_l:
        value = goal_l.split("by", 1)[1].strip()

        return {
            "action": "execute_plan",
            "plan": [
                {
                    "action": "click_video",
                    "mode": "channel",
                    "value": value
                }
            ]
        }

    if "titled" in goal_l:
        value = goal_l.split("titled", 1)[1].strip()

        return {
            "action": "execute_plan",
            "plan": [
                {
                    "action": "click_video",
                    "mode": "title",
                    "value": value
                }
            ]
        }

    return None