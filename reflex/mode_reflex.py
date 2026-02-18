from reflex.mode_registry import MODES

def handle_mode(goal_l):

    for mode_name in MODES:

        if f"{mode_name} mode" in goal_l:

            mode = MODES[mode_name]
            plan = []

            # 1️⃣ Open folder if exists
            if "folder" in mode:
                plan.append({
                    "action": "open_app",
                    "cmd": f'explorer "{mode["folder"]}"'
                })

            # 2️⃣ Open app if exists
            if "app_path" in mode:
                plan.append({
                    "action": "open_app",
                    "cmd": f'"{mode["app_path"]}"'
                })

            # 3️⃣ Spotify
            if "spotify_uri" in mode:
                plan.append({
                    "action": "open_uri",
                    "uri": mode["spotify_uri"]
                })

            # 4️⃣ Chrome
            if "chrome_url" in mode:
                plan.append({
                    "action": "open_app",
                    "cmd": f'{mode["chrome_path"]} "{mode["chrome_url"]}"'
                })

            return {
                "action": "execute_plan",
                "plan": plan
            }

    return None
