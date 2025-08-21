#!/usr/bin/env python3

import sys
import subprocess
import json
from vosk import Model, KaldiRecognizer, SetLogLevel

# ------ config ----------
VOSK_MODEL_PATH = "stt/vosk-model-en-us-0.42-gigaspeech" # Set your Vosk model path here
SAMPLE_RATE = 16000
CHUNK_DURATION_SEC = 20
# ------------------------

BYTES_PER_SECOND = SAMPLE_RATE * 2  # 16-bit audio = 2 bytes per sample
CHUNK_SIZE = CHUNK_DURATION_SEC * BYTES_PER_SECOND  # secs of audio

def transcribe_chunk(model, chunk_data):
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)
    if rec.AcceptWaveform(chunk_data):
        result = json.loads(rec.Result())
        return result.get("text", "")
    return ""

def main():
    if sys.stdin.isatty():
        print("[-] This script expects audio piped in via stdin.", file=sys.stderr)
        sys.exit(1)

    model = Model(VOSK_MODEL_PATH)
    audio_input = sys.stdin.buffer

    while True:
        chunk = audio_input.read(CHUNK_SIZE)
        if not chunk:
            break
        text = transcribe_chunk(model, chunk)
        if text.strip():
            print(text, flush=True)

if __name__ == "__main__":
    SetLogLevel(-1)
    main()
