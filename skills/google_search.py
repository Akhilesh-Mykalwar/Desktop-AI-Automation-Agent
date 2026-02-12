from skills.base import Skill
from app_registry import SYSTEM_APPS

class GoogleSearchSkill(Skill):
    name = "google_search"

    def can_handle(self, intent: dict) -> bool:
        return (
            intent.get("intent") == "search"
            and intent.get("app") == "google"
            and intent.get("track_name")
        )

    def build_plan(self, intent: dict) -> list:
        query = intent["track_name"]
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

        cmd = SYSTEM_APPS["google"]["cmd"]

        if intent.get("incognito"):
            cmd = f'{cmd} --incognito "{url}"'
        else:
            cmd = f'{cmd} "{url}"'

        return [
            {
                "action": "open_app",
                "cmd": cmd
            }
        ]
