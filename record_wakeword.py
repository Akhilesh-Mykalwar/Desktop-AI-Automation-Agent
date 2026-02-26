import sounddevice as sd
import soundfile as sf
import os
import time

SAMPLE_RATE = 16000
DURATION = 2  # seconds
CHANNELS = 1

def record_sample(folder, index, phrase):
    print(f"\nSample {index + 1}")
    print(f"Say: '{phrase}'")
    print("Recording in 1 second...")
    time.sleep(1)

    audio = sd.rec(int(DURATION * SAMPLE_RATE),
                   samplerate=SAMPLE_RATE,
                   channels=CHANNELS,
                   dtype="float32")
    sd.wait()

    filepath = os.path.join(folder, f"sample_{index}.wav")
    sf.write(filepath, audio, SAMPLE_RATE)
    print("Saved:", filepath)

def record_set(base_folder, phrase, count):
    os.makedirs(base_folder, exist_ok=True)
    for i in range(count):
        input("Press Enter to record...")
        record_sample(base_folder, i, phrase)

if __name__ == "__main__":
    print("Wake Word Recorder")

    print("\n1) Record Yo Sorenza")
    record_set("Voice Training/Sorenza/positive", "yo sorenza", 50)

    print("\n2) Record Sir Godfrey")
    record_set("Voice Training/Godfrey/positive", "sir godfrey", 50)