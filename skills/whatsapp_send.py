from skills.base import Skill

class WhatsAppSendMessageSkill(Skill):
    name = "whatsapp_send"

    def can_handle(self, intent: dict) -> bool:
        return (
            intent.get("send_message") is True
            and intent.get("message")
        )

    def build_plan(self, intent: dict) -> list:
        return [
            {"action": "wait", "time": 0.5},
            {"action": "type", "text": intent["message"]},
            {"action": "press", "key": "enter"}
        ]
