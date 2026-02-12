from skills.base import Skill
from app_registry import SYSTEM_APPS

class WhatsAppSearchSkill(Skill):
    name = "whatsapp_search"

    def can_handle(self, intent: dict) -> bool:
        return (
            intent.get("intent") == "search"
            and intent.get("app") == "whatsapp"
            and intent.get("track_name")
        )

    def build_plan(self, intent: dict) -> list:
        query = intent["track_name"]

        return [
            # 1️⃣ open WhatsApp
  

            # 2️⃣ let it focus
            {
                "action": "wait",
                "time": 0.8
            },

            # 3️⃣ search chats
            {
                "action": "hotkey",
                "keys": ["ctrl", "f"]
            },

            # 4️⃣ type contact name
            {
                "action": "type",
                "text": query
            },

            # 5️⃣ open chat
            {
                "action": "press",
                "key": "enter"
            }
        ]
