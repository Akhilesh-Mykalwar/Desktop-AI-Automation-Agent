from skills.base import Skill
from app_registry import SYSTEM_APPS

class YouTubeSearchSkill(Skill):
    name = "youtube_search"

    def can_handle(self, intent):
        return (
            intent.get("intent") == "search"
            and intent.get("app") == "youtube"
            and intent.get("track_name")
        )

    def build_plan(self, intent):
        query = intent["track_name"]

        return [
         
            {
                "action": "wait",
                "time": 1.5
            },
            {
                "action": "press",
                "key": "/"
            },
            {
                "action": "type",
                "text": intent["track_name"]
            },
            {
                "action": "press",
                "key": "enter"
            },
            {
                "action": "wait",
                "time": 0.8
            }
        ]

