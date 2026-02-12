import pytesseract
import cv2
import numpy as np
from PIL import ImageGrab

import re

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]', '', text)  # remove spaces, dashes, symbols
    return text


def find_text_on_screen(target_text):
    screenshot = ImageGrab.grab()
    img = np.array(screenshot)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

    target_text = target_text.lower()

    for i, word in enumerate(data["text"]):
        word_clean = word.strip().lower()

        if target_text in word_clean and word_clean != "":
            x = data["left"][i]
            y = data["top"][i]
            w = data["width"][i]
            h = data["height"][i]

            center_x = x + w // 2
            center_y = y + h // 2

            return center_x, center_y

    return None



def get_all_text_blocks():
    screenshot = ImageGrab.grab()
    img = np.array(screenshot)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply contrast BEFORE OCR
    gray = cv2.convertScaleAbs(gray, alpha=1.7, beta=10)

    # Optional slight blur to reduce noise
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

    blocks = []

    for i, word in enumerate(data["text"]):
        word_clean = word.strip()

        if word_clean == "":
            continue

        confidence = int(data["conf"][i])
        if confidence < 30:
            continue

        x = data["left"][i]
        y = data["top"][i]
        w = data["width"][i]
        h = data["height"][i]

        blocks.append({
            "text": word_clean.lower(),
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "center_x": x + w // 2,
            "center_y": y + h // 2,
            "confidence": confidence
        })

    return blocks


def group_words_into_lines(blocks, y_threshold=5):
    """
    Merge nearby words into horizontal text lines.
    """

    # sort by vertical position first
    blocks = sorted(blocks, key=lambda b: b["y"])

    lines = []

    for block in blocks:
        placed = False

        for line in lines:
            # if this word is close vertically to existing line
            if (abs(block["y"] - line["y"]) < y_threshold and abs(block["x"] - line["words"][-1]["x"]) < 100):
                line["words"].append(block)
                placed = True
                break

        if not placed:
            lines.append({
                "y": block["y"],
                "words": [block]
            })

    # build merged lines
    merged = []

    for line in lines:
        words_sorted = sorted(line["words"], key=lambda w: w["x"])
        full_text = " ".join(w["text"] for w in words_sorted)

        merged.append({
            "text": full_text,
            "y": line["y"],
            "x": words_sorted[0]["x"],
            "center_x": words_sorted[0]["center_x"],
            "center_y": words_sorted[0]["center_y"]
        })

    return merged


def find_first_video_title():
    blocks = get_all_text_blocks()
    lines = group_words_into_lines(blocks)

    candidates = []

    for line in lines:
        if line["y"] < 200:
            continue
        if line["x"] < 200:
            continue
        if len(line["text"]) < 10:
            continue
        if "views" in line["text"]:
            continue
        if "ago" in line["text"]:
            continue
        if len(line["text"].split()) < 3:
            continue
        candidates.append(line)

    if not candidates:
        return None

    # Step 1: find top row (smallest Y)
    candidates.sort(key=lambda l: l["y"])
    top_y = candidates[0]["y"]

    # Step 2: collect all titles within same row band
    same_row = [
        c for c in candidates
        if abs(c["y"] - top_y) < 20
    ]

    # Step 3: pick leftmost from that row
    same_row.sort(key=lambda l: l["x"])

    return same_row[0]

def find_video_by_title(target_title):
    target_title = target_title.lower()

    blocks = get_all_text_blocks()
    lines = group_words_into_lines(blocks)

    candidates = []

    for line in lines:
        if line["y"] < 200:
            continue
        if line["x"] < 200:
            continue
        if len(line["text"]) < 10:
            continue

        if target_title in line["text"]:
            candidates.append(line)

    if not candidates:
        return None

    # pick top-most match
    candidates.sort(key=lambda l: (l["y"], l["x"]))

    return candidates[0]

def find_video_by_channel(channel_name):
    channel_name_norm = normalize_text(channel_name)

    blocks = get_all_text_blocks()
    lines = group_words_into_lines(blocks)

    matches = []

    for line in lines:

        # remove header
        if line["y"] < 200:
            continue

        # remove sidebar-ish region
        if line["x"] < 180:
            continue

        # remove obvious metadata junk
        if "views" in line["text"]:
            continue
        if "ago" in line["text"]:
            continue

        line_norm = normalize_text(line["text"])

        if channel_name_norm in line_norm:
            matches.append(line)

    if not matches:
        return None

    matches.sort(key=lambda l: (l["y"], l["x"]))

    channel_line = matches[0]

    return {
        "center_x": channel_line["center_x"],
        "center_y": channel_line["center_y"] - 25,
        "text": channel_line["text"]
    }

