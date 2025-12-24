## Project Structure```
.
├── Cargo.toml                 # Rust workspace configuration
├── config.toml                # Configuration file for the pipeline
├── create-ollama-model.sh     # Script to create Ollama models from Hugging Face GGUF files
├── pipeline                   # Rust binary (compiled from main.rs)
├── pipeline-project/          # Rust workspace directory
│   ├── src/
│   │   └── main.rs            # Main Rust application logic
│   └── Cargo.toml             # Rust project configuration
├── project_script.sh          # Script to run the full pipeline with custom prompts
├── requirements.txt           # Python dependencies
├── setup.sh                   # Installation and setup script
├── system.log                 # Log file showing execution history
└── voice.py                   # Python module for STT/TTS functionality
```## File Descriptions

### `Cargo.toml`
**Purpose**: Rust workspace configuration file

**Details**:
- Defines a workspace with resolver version 3
- Includes `pipeline-project` as a member
- This is a minimal configuration for a Rust workspace

### `config.toml`
**Purpose**: Configuration file for the pipeline

**Details**:```toml
[workspace]
resolver = "3"

members = [
    "pipeline-project",
]
```**Configuration Options**:
- `python_env`: Path to Python executable (e.g., "./env/bin/python3")
- `audio_file`: Input audio file path (e.g., "./misc/space.wav")
- `llm_model`: LLM model name and tag (e.g., "capybarahermes-2.5-mistral-7b.Q4_0:latest")
- `tts_model`: TTS voice model (e.g., "af_heart")
- `output`: Output audio file path (e.g., "./things/llm-output.wav")
- `stt_model`: STT model name (e.g., "tiny")
- `stt_lang`: STT language code (e.g., "en")
- `log_file`: Path to log file (e.g., "system.log")
- `enable_logging`: Boolean flag to enable/disable logging

### `create-ollama-model.sh`
**Purpose**: Script to create Ollama models from Hugging Face GGUF files

**Details**:
- Takes a Hugging Face GGUF file URL as command-line argument
- Downloads the GGUF file
- Creates a Modelfile with a custom system prompt
- Creates the Ollama model using `ollama create`
- Cleans up temporary files

**Usage**:```sh
./create-ollama-model.sh https://huggingface.co/TheBloke/CapybaraHermes-2.5-Mistral-7B-GGUF/resolve/main/capybarahermes-2.5-mistral-7b.Q4_0.gguf?download=true
```**System Prompt**: The script creates a system prompt that makes the AI communicate like a thoughtful, attentive human during voice calls or real-life conversations with natural language, contractions, and appropriate tone.

### `pipeline` (Rust Binary)
**Purpose**: Main application binary for the voice assistant pipeline

**Details**:
- Command-line interface built with `clap`
- Implements full pipeline: STT → LLM → TTS
- Uses `tokio` for async operations
- Reads configuration from `config.toml`
- Logs execution to `system.log`

**Commands**:
1. `stt [input]` - Run speech-to-text only
   - `input`: Input audio file or device path (e.g., 'input.wav' or '/dev/audio')
2. `llm [input]` - Run LLM processing
   - `input`: Input text for LLM processing
3. `tts [input]` - Run text-to-speech only
   - `input`: Input text for TTS processing

**Functions**:
- `run_stt(input)`: Executes Python STT script with specified model and language
- `run_llm(input)`: Runs Ollama LLM with specified model and input text
- `run_tts(input)`: Executes Python TTS script with specified voice model and output file
- `log(message)`: Writes timestamped log entries to configured log file
- `get_config()`: Returns global configuration instance

### `project_script.sh`
**Purpose**: Script to run custom pipeline workflows with specific prompts

**Details**:
- Configurable prompt and function group selection
- Supports multiple workflow patterns (arithmetic, bird_net, etc.)
- Creates temporary files for pipeline stages
- Executes pipeline in sequence: STT → LLM → FES (Function Execution Service) → LLM → TTS

**Key Variables**:
- `prompt_id`: Numeric identifier for the prompt to use
- `function_group`: Group of functions to execute (e.g., "arithmetic")
- `WORKLOAD_DIR`: Directory containing workload files
- `AI_PIPELINE_BIN`: Path to the pipeline binary
- `FES_BIN`: Path to the function execution service binary

**Workflow**:
1. Reads original prompt from workload directory
2. Gets FES functions from workload directory
3. Reads base prompts for formatting
4. Creates temporary files with combined prompts
5. Runs LLM processing on first prompt
6. Executes FES on LLM output to find and run functions
7. Creates secondary prompt with FES results
8. Runs LLM processing on secondary prompt
9. Executes TTS on final LLM output

### `requirements.txt`
**Purpose**: Python dependencies for the voice assistant

**Details**:
- `openai-whisper`: Speech recognition library
- `kokoro`: Text-to-speech library
- `sounddevice`: Audio input/output
- `pyaudio`: Audio I/O library
- `numpy`: Numerical computing
- `soundfile`: Audio file I/O

### `setup.sh`
**Purpose**: Installation and setup script for the entire pipeline

**Details**:
- Updates system packages and installs required tools
- Installs Rust using rustup
- Builds Rust pipeline project in release mode
- Sets up Python virtual environment
- Installs Python dependencies
- Installs Ollama
- Provides usage instructions after setup

**Steps**:
1. Updates system packages
2. Installs system dependencies (Python, Rust, FFmpeg, etc.)
3. Installs Rust using curl script
4. Builds Rust pipeline binary
5. Creates Python virtual environment
6. Installs Python dependencies
7. Installs Ollama
8. Shows usage instructions

### `system.log`
**Purpose**: Execution log file showing pipeline runs

**Details**:
- Contains timestamped log entries for each pipeline execution
- Shows STT, LLM, and TTS processing completion
- Includes error messages and execution times
- Records multiple pipeline runs with timestamps

**Example Format**:```
[2025-11-19 16:03:31.715] Script started
[2025-11-19 16:03:31.716] Running full pipeline
[2025-11-19 16:03:36.418] STT processing completed
[2025-11-19 16:03:36.418] Starting LLM processing
[2025-11-19 16:04:04.824] LLM processing completed
[2025-11-19 16:04:04.831] Starting TTS processing
[2025-11-19 16:04:23.095] TTS processing completed
[2025-11-19 16:04:23.096] Script execution completed
```### `voice.py`
**Purpose**: Python module for STT/TTS functionality

**Details**:
- Implements speech-to-text and text-to-speech operations
- Uses Whisper for STT and Kokoro for TTS
- Supports multiple languages and voice models
- Includes error handling and logging

**Key Functions**:
1. `run_tts(text, voice, speed, output_file)`:
   - Converts text to speech using Kokoro TTS engine
   - Supports voice selection from predefined TTS voices
   - Accepts speed parameter for speech rate
   - Can save output to file or play directly

2. `run_stt(model_name, language, input_file)`:
   - Converts audio file to text using Whisper
   - Supports multiple STT models (tiny, base, small, medium, large)
   - Handles language selection
   - Groups sentences into paragraphs for better readability

3. `download_model(model_name)`:
   - Downloads Whisper model to local cache directory
   - Creates necessary directories
   - Handles model caching

**Command-line Interface**:
- `tts`: Text-to-speech conversion
  - `-v, --voice`: Voice model (default: af_heart)
  - `-i, --input-file`: Input text file path
  - `-o, --output-file`: Output audio file path
  - `-s, --speed`: Speech speed (default: 1.2)
  - `text`: Text to convert to speech (positional argument)

- `stt`: Speech-to-text conversion
  - `-m, --model`: Speech recognition model (required)
  - `-l, --language`: Language for speech recognition (default: en)
  - `file`: Input audio file path (positional argument)

- `download`: Download a speech recognition model
  - `-m, --model`: Model to download (required)

**Supported Voices**:
- English voices: af_heart, af_alloy, af_aoede, af_bella, af_jessica, af_kore, af_nicole, af_nova, af_river, af_sarah, af_sky
- Male voices: am_adam, am_echo, am_eric, am_fenrir, am_liam, am_michael, am_onyx, am_puck, am_santa
- Female voices: bf_alice, bf_emma, bf_isabella, bf_lily, bm_daniel, bm_fable, bm_george, bm_lewis
- Other voices: ef_dora, em_alex, em_santa, ff_siwis, hf_alpha, hf_beta, hm_omega, hm_psi, if_sara, im_nicola, pf_dora, pm_alex, pm_santa

**Supported STT Models**:
- tiny: ~75 MB
- base: ~151 MB
- small: ~488 MB
- medium: ~1.5 GB
- large: ~2.9 GB

## Setup and Usage

1. Run setup script: `./setup.sh`
2. Configure `config.toml` with desired settings
3. Run pipeline with: `./pipeline` (full pipeline) or `./pipeline [command]` (specific stage)

The pipeline supports both automated execution and manual command-line operations for each stage of the voice assistant workflow.
