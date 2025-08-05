#!/usr/bin/env bash

# update and install tools
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip ffmpeg build-essential -y

# setup and enter python env
python3 -m venv python-env
source python-env/bin/activate

# install script dependencies
pip install vosk
pip install numpy

# find vosk model https://alphacephei.com/vosk/models
# default: vosk-model-small-en-us-0.15
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
rm vosk-model-small-en-us-0.15.zip

# setup model to build
ollama create convo-ai -f Modelfile
