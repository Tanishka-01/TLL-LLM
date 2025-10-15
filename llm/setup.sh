#!/usr/bin/env bash

# update and install tools
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3.12-venv portaudio19-dev ffmpeg build-essential curl -y

### rust
# install and setup rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# build ai pipeline
cargo build --release
cp ./target/release/pipeline pipeline

### python
# setup and enter python env
python3 -m venv env
source env/bin/activate

# install script dependencies
pip install --no-cache-dir -r requirements.txt

### ollama
# install ollama
curl -fsSL https://ollama.com/install.sh | sh

# how to use the program
echo -e "\nHello! the script has finished.\nPlease run the pipeline executable to see that to do next. [./pipeline -h]"

