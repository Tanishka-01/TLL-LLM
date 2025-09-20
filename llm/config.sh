### config for real time LLM communication pipeline 
# Python Environment
PYTHON_ENV="./python-env/bin/python3"

# LLM Settings
LLM_MODEL="capybarahermes-2.5-mistral-7b.Q4_0:latest"

# TTS Settings
TTS_MODEL="af_heart"
OUTPUT="llm-output.wav"

# STT Settings
STT_MODEL="tiny"
STT_LANG="en"

# Logging Settings
LOG_FILE="system.log"
ENABLE_LOGGING=true

# unused for now
SAMPLE_RATE=16000
CHUNK_DURATION_SEC=20

AUDIO_FILE="./output.wav"
