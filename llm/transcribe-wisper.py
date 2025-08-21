#!/usr/bin/env python3

import sys
import subprocess
import json
from whisper import load_model, transcribe

# ------ config ----------
WHISPER_MODEL = "base"  # Options: 'tiny', 'base', 'small', 'medium', 'large'
SAMPLE_RATE = 16000
CHUNK_DURATION_SEC = 20
# ------------------------

BYTES_PER_SECOND = SAMPLE_RATE * 2  # 16-bit audio = 2 bytes per sample
CHUNK_SIZE = CHUNK_DURATION_SEC * BYTES_PER_SECOND  # secs of audio

def transcribe_chunk(model, chunk_data):
    import io
    from scipy.io.wavfile import write

    # Write the chunk data to a temporary WAV file
    with io.BytesIO() as wav_file:
        write(wav_file, SAMPLE_RATE, (chunk_data.reshape(-1, 2) / 32768.0).astype('float32'))
        wav_file.seek(0)
        result = transcribe(model, wav_file, language='en', fp16=False)
    return result['text']

def main():
    if sys.stdin.isatty():
        print("[-] This script expects audio piped in via stdin.", file=sys.stderr)
        sys.exit(1)

    model = load_model(WHISPER_MODEL)
    audio_input = sys.stdin.buffer

    while True:
        chunk = audio_input.read(CHUNK_SIZE)
        if not chunk:
            break
        text = transcribe_chunk(model, chunk)
        if text.strip():
            print(text, flush=True)

if __name__ == "__main__":
    main()
