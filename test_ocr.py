import time
import pyautogui
from scroll  import universal_scroll 


from vision_ocr import (
    get_all_text_blocks,
    group_words_into_lines,
    find_video_by_channel,
    normalize_text
)

print("⏳ Switching in 1 second...")
time.sleep(1)

channel_to_search = "yub"
channel_norm = normalize_text(channel_to_search)

print("\n🔎 Searching for channel:", channel_to_search)
universal_scroll("down")
print("Normalized search:", channel_norm)
print("\n--- OCR MERGED LINES ---\n")

blocks = get_all_text_blocks()
lines = group_words_into_lines(blocks)

for line in lines:
    if line["y"] < 200:
        continue

    line_norm = normalize_text(line["text"])

    print(f"Y:{line['y']}  X:{line['x']}")
    print("RAW: ", line["text"])
    print("NORM:", line_norm)
    print("MATCH:", channel_norm in line_norm)
    print("-" * 50)

print("\n--- FINAL MATCH ATTEMPT ---\n")

result = find_video_by_channel(channel_to_search)

if result:
    print("Clicking:", result["text"])
    pyautogui.click(result["center_x"], result["center_y"])
else:
    print("No match found")