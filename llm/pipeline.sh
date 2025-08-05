#!/usr/bin/env bash

ffmpeg -i dbd_debate.mp4 -f s16le -acodec pcm_s16le -ac 1 -ar 16000 - 2>/dev/null | \
#python3 transcribe.py 2>/dev/null | \
python3 transcribe.py | \
#while read -r chunk; do
  #echo "$chunk" | ollama run convo-ai
#done
while read -r chunk; do
  echo "$chunk" | cat
done
