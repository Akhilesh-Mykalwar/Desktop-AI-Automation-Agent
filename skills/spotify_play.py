from skills.base import Skill
from app_registry import SYSTEM_APPS, SPOTIFY_PLAYLISTS


class SpotifyPlaySkill(Skill):
    name = "spotify_play"

    def can_handle(self, intent: dict) -> bool:
        return intent.get("intent") == "play_spotify"

    def build_plan(self, intent: dict) -> list:
        playlist = (intent.get("playlist") or "").lower()
        track_name = (intent.get("track_name") or "").lower()

        plan = []

        # 1️⃣ Open Spotify
        # plan.append({
        #     "action": "open_app",
        #     "cmd": SYSTEM_APPS["spotify"]["cmd"]
        # })

        # 2️⃣ Open playlist (if provided)
        if playlist in SPOTIFY_PLAYLISTS:
            playlist_id = SPOTIFY_PLAYLISTS[playlist]["id"]
            plan.append({
                "action": "open_uri",
                "uri": f"spotify:playlist:{playlist_id}"
            })

        # 3️⃣ Let Spotify focus
        plan.append({
            "action": "wait",
            "time": 1.5
        })

        # 4️⃣ Start playback
        plan.append({
            "action": "press",
            "key": "space"
        })

        # 5️⃣ Optional: play specific song
        if track_name:
            plan.extend([
                {"action": "hotkey", "keys": ["ctrl", "l"]},
                {"action": "type", "text": track_name},
                {"action": "press", "key": "enter"},
                {"action": "wait", "time": 0.8},
                {"action": "press", "key": "down"},
                {"action": "press", "key": "space"}
            ])

        return plan

    # 🔑 THIS IS THE MISSING PIECE
   