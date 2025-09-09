#!/usr/bin/env bash

# update and install tools
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip ffmpeg build-essential -y

# setup and enter python env
python3 -m venv python-env
source python-env/bin/activate

# install script dependencies
pip install -r requirements.txt

# setup model to build
ollama create convo-ai -f Modelfile
