🎙️ Voice Pipeline

A full-stack voice processing pipeline that converts audio input to text using AI, processes it with a local or remote LLM, and then converts the output back to audio for playback or storage.

🚀 Overview

This project is a complete end-to-end pipeline for:

1. Speech to Text – Convert audio input to text using [OpenAI's Whisper](https://github.com/openai/whisper).
2. LLM Processing – Use a local or remote Large Language Model (LLM) via [Ollama CLI](https://ollama.com/) and models from [Hugging Face](https://huggingface.co/).
3. Text to Speech – Convert the LLM's output text back to audio using [Kokoro](https://github.com/hexgrad/kokoro).

The pipeline is controlled via a clean CLI built with Rust, and it's highly configurable through a config.toml file.

📦 Dependencies

Rust
• Clap: For building a clean CLI.
• Chrono: For handling Unix timestamps.
• Serde: For serialization and deserialization.
• Toml: For parsing TOML configuration files.

Python
• Whisper: For speech-to-text.
• Kokoro: For text-to-speech.

Ollama
• Ollama CLI: For running local LLMs from Hugging Face.

🛠️ Setup Instructions

1. **Clone the repository**:
``` bash
   git clone https://github.com/your-username/your-project-name.git
```
2. **Install dependencies**:
``` bash
   ./setup.sh
```
3. **Configure your pipeline**:
   - Modify config.toml to set your preferred LLM, audio input/output formats, and other settings.
4. **4. Run the pipeline**:
``` bash
    ./pipeline
```

All pipeline activity, errors, and warnings are logged in system.log for easy debugging and monitoring.
