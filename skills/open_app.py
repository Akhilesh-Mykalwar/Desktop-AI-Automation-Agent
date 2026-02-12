from skills.base import Skill
from app_registry import SYSTEM_APPS

class OpenAppSkill(Skill):
    name = "open_app"

    def can_handle(self, intent: dict) -> bool:
        return (
            intent.get("intent") == "open_app"
            and intent.get("app") in SYSTEM_APPS
        )

   
class OpenAppSkill(Skill):
    name = "open_app"

    def can_handle(self, intent):
        return intent.get("intent") == "open_app" and intent.get("app") in SYSTEM_APPS

    def build_plan(self, intent):
        app = SYSTEM_APPS[intent["app"]]

        if app["type"] == "exe" or app["type"] == "app_mode":
            return [{
                "action": "open_app",
                "cmd": app["cmd"]
            }]

        elif app["type"] == "uwp":
            return [{
                "action": "open_uwp",
                "name": app["id"]
            }]

        return []



      