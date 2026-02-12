from skills.base import Skill
from app_registry import SYSTEM_APPS

class DiscordVoiceSkill(Skill):
    name = "discord_voice"

    def can_handle(self, intent: dict) -> bool:
        return intent.get("intent") == "join_voice" and intent.get("app") == "discord"

    def build_plan(self, intent: dict) -> list:
        channel = intent.get("channel", "")

        return [
            # 1️⃣ open discord
            {
                "action": "open_app",
                "cmd": SYSTEM_APPS["discord"]["cmd"]
            },

            {"action": "wait", "time": 0.5},

            # 2️⃣ quick switcher
            {"action": "hotkey", "keys": ["ctrl", "k"]},
            {"action": "wait", "time": 0.3},

            {"action": "type", "text": channel},
            {"action": "press", "key": "enter"},

            {"action": "wait", "time": 1.0}
        ]
