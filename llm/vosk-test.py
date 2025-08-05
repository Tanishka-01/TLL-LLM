#!/usr/bin/env bash

ffmpeg -i dbd_debate.mp4 -f s16le -acodec pcm_s16le -ac 1 -ar 16000 - > output-file.txt #2>/dev/null
