from gpt4all import GPT4All
import json
import re

from app_registry import SYSTEM_APPS

from skills.open_app import OpenAppSkill
from skills.spotify_play import SpotifyPlaySkill
from skills.youtube_search import YouTubeSearchSkill
from skills.whatsapp_search import WhatsAppSearchSkill
from skills.whatsapp_send import WhatsAppSendMessageSkill
from skills.discord_voice import DiscordVoiceSkill
from skills.google_search import GoogleSearchSkill

from reflex.reflex_engine import check_reflex

# ------------------------
# LLM SETUP — lazy loaded
# ------------------------

MODEL_NAME = "Phi-3-mini-4k-instruct-q4.gguf"
MODEL_PATH = r"C:\Users\Akhil\OneDrive\Desktop\AI\Desktop AI Assistant\Models"

_model = None  # not loaded yet

def _get_model():
    """Load the model on first use, then cache it."""
    global _model
    if _model is None:
        print("⏳ Loading model...")
        _model = GPT4All(
            model_name=MODEL_NAME,
            model_path=MODEL_PATH,
            allow_download=False
        )
        print("✅ Model ready.")
    return _model


# ------------------------
# SYSTEM PROMPT
# ------------------------

SYSTEM_PROMPT = """
Extract intent from the goal.

Return ONLY valid JSON:
{
 "intent": "open_app | search | join_voice",
 "app": "discord | whatsapp | youtube | spotify | google | other",
 "track_name": "",
 "server": "",
 "channel": ""
}

Rules:
- If goal says "search" → intent = search
- If goal says "open" → intent = open_app
- If goal says "join voice" or "connect" on Discord → intent = join_voice
- All text must be lowercase
- If unsure, leave fields empty
"""


# ------------------------
# HELPERS
# ------------------------

def extract_json(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else None


def parse_goal(goal: str) -> dict:
    prompt = f"{SYSTEM_PROMPT}\nGoal: {goal}"
    output = _get_model().generate(prompt, max_tokens=64, temp=0)

    json_text = extract_json(output)
    if not json_text:
        return {}

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        return {}

    for key in ("intent", "app"):
        val = data.get(key)
        if isinstance(val, str) and "|" in val:
            data[key] = val.split("|")[0].strip()

    return data


def normalize_intent(intent: dict, goal: str) -> dict:
    goal_l = goal.lower()

    if not intent:
        intent = {}

    if not intent.get("app"):
        if "whatsapp" in goal_l:
            intent["app"] = "whatsapp"
        elif "youtube" in goal_l:
            intent["app"] = "youtube"
        elif "spotify" in goal_l:
            intent["app"] = "spotify"
        elif "discord" in goal_l:
            intent["app"] = "discord"
        elif "google" in goal_l or "chrome" in goal_l:
            intent["app"] = "google"

    if "spotify" in goal_l:
        intent["app"] = "spotify"
        if "play" in goal_l or "start" in goal_l or "resume" in goal_l:
            intent["intent"] = "play_spotify"
            words = goal_l.split("playlist", 1)
            if len(words) > 1:
                intent["playlist"] = words[1].strip()

    if "search" in goal_l:
        intent["intent"] = "search"
        after = goal_l.split("search", 1)[1].strip()
        for prefix in ("for ", "about ", "on "):
            if after.startswith(prefix):
                after = after[len(prefix):]
        if after:
            intent["track_name"] = after

    if "incognito" in goal_l:
        intent["incognito"] = True

    if "send" in goal_l:
        intent["send_message"] = True
        after_send = goal_l.split("send", 1)[1].strip()
        intent["message"] = after_send
        if intent.get("track_name"):
            intent["track_name"] = intent["track_name"].split("and send")[0].strip()

    if "discord" in goal_l and (
        "join" in goal_l or "voice" in goal_l or "connect" in goal_l
    ):
        intent["intent"] = "join_voice"
        words = goal_l.split()
        if "join" in words:
            idx = words.index("join")
            if idx + 1 < len(words):
                intent["channel"] = words[idx + 1]

    return intent


# ------------------------
# SKILLS
# ------------------------

SKILLS = [
    OpenAppSkill(),
    WhatsAppSearchSkill(),
    WhatsAppSendMessageSkill(),
    DiscordVoiceSkill(),
    SpotifyPlaySkill(),
    YouTubeSearchSkill(),
    GoogleSearchSkill()
]


# ------------------------
# PLANNER CORE
# ------------------------

def decide_next_action(goal, history):

    # 1️⃣ Reflex layer — no model needed, runs instantly
    reflex_result = check_reflex(goal)
    if reflex_result:
        return reflex_result

    # 2️⃣ AI layer — model loaded here on first call only
    intent = parse_goal(goal)
    intent = normalize_intent(intent, goal)
    print("🧠 NORMALIZED INTENT:", intent)

    plans = []

    if intent.get("app") and not (
        intent.get("intent") == "search"
        and intent.get("app") == "google"
    ):
        open_intent = {"intent": "open_app", "app": intent["app"]}
        for skill in SKILLS:
            if skill.can_handle(open_intent):
                plans.extend(skill.build_plan(open_intent))
                break

    if intent.get("intent") == "search":
        for skill in SKILLS:
            if skill.can_handle(intent):
                plans.extend(skill.build_plan(intent))
                break

    if intent.get("send_message") and intent.get("message"):
        plans.extend([
            {"action": "wait", "time": 0.5},
            {"action": "type", "text": intent["message"]},
            {"action": "press", "key": "enter"}
        ])

    if intent.get("intent") == "play_spotify":
        for skill in SKILLS:
            if skill.can_handle(intent):
                plans.extend(skill.build_plan(intent))
                break

    if intent.get("intent") == "join_voice":
        for skill in SKILLS:
            if skill.can_handle(intent):
                plans.extend(skill.build_plan(intent))
                break

    print("📦 FINAL PLAN:", plans)

    if plans:
        return {"action": "execute_plan", "plan": plans}

    return {"action": "done"}