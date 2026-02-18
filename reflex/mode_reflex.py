from reflex.mode_registry import WORK_MODE

def handle_mode(goal_l):

    triggers = [
        "switch to work mode",
        "activate work mode",
        "enter work mode",
        "work mode"
    ]

    if not any(trigger in goal_l for trigger in triggers):
        return None

    return {
        "action": "execute_plan",
        "plan": [

            # 1️⃣ Open folder
            {
                "action": "open_app",
                "cmd": f'explorer "{WORK_MODE["folder"]}"'
            },

            # 2️⃣ Open Spotify playlist
            {
                "action": "open_uri",
                "uri": WORK_MODE["spotify_uri"]
            },

            # 3️⃣ Open ChatGPT in Chrome
            {
                "action": "open_app",
                "cmd": f'{WORK_MODE["chrome_path"]} "{WORK_MODE["chatgpt_url"]}"'
            }
        ]
    }
