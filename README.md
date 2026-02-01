# Tightlipped LLM

A local voice assistant that routes queries to the safest AI service based on who you are. A lawyer's client details stay on-device. A journalist's source information never leaves the machine. General knowledge questions go to the cloud for better answers.

The system uses a local 7B model as a gatekeeper — the **Tight-Lipped Layer (TLL)** — to make routing decisions *before* any data leaves your device.

## How It Works

```
Voice In → STT → [TLL decides: LOCAL or CLOUD?] → LLM → TTS → Voice Out
```

1. **STT** (Whisper) converts speech to text
2. **TLL** reads the text + your profile and decides where to send it
3. **LLM** (Ollama) processes the query locally or the decision indicates a cloud service
4. **TTS** (Kokoro) speaks the response back

## The Tight-Lipped Layer (TLL)

The TLL is a privacy-aware routing layer that sits between the user and the LLM. It takes two inputs — a **query** and a **profile** — and outputs a routing decision.

### Core Idea: Relative Sensitivity

The same words carry different risk depending on who says them:

- "Meeting at Blue Duck Tavern, 6pm" from a **journalist** → **LOCAL** (could expose a source)
- "Meeting at Blue Duck Tavern, 6pm" from a **healthcare worker** → **Cloud** (just dinner plans)
- "Patient John Smith, MRN-4521" from a **healthcare worker** → **LOCAL** (HIPAA violation if leaked)
- "What are neuropathy symptoms?" from **anyone** → **Cloud** (public knowledge)

### The Four Profiles

| Profile | Protects | Triggers LOCAL |
|---------|----------|----------------|
| **Lawyer** | Client identity, case strategy, privileged communications | Any client name, case detail, or legal strategy |
| **Journalist** | Source identity, meeting details, investigation targets | Any source, meeting detail, or investigation target |
| **Healthcare** | Patient identity + medical info (HIPAA) | Any patient name, ID, or identifiable medical record |
| **Researcher** | Unpublished results, proprietary methods | Any unpublished data, proprietary method, or competitive benchmark |

### Conflict Detection

If a query is adversarial to a company, that company's AI service is blocked:

- Suing **Google** → block Gemini
- Investigating **Anthropic** → block Claude
- Competing with **OpenAI/Microsoft** → block OpenAI

### Available Services

| Service | Provider | When to use |
|---------|----------|-------------|
| **LOCAL** | Your device (Ollama) | Sensitive queries — always safe |
| **Claude** | Anthropic | Non-sensitive, no Anthropic conflict |
| **OpenAI** | OpenAI/Microsoft | Non-sensitive, no OpenAI/Microsoft conflict |
| **Gemini** | Google/Alphabet | Non-sensitive, no Google conflict |

### Hard Rule

If a query contains **any** sensitive information for the given profile, it routes to **LOCAL**. No exceptions. Cloud services can be subpoenaed, breached, or logged. LOCAL guarantees zero data exposure.

## Project Structure

```
llm/
├── tll.py                          # Tight-Lipped Layer (routing logic)
├── pipeline                        # Compiled Rust binary (CLI)
├── pipeline-project/src/main.rs    # Rust source (STT, LLM, TTS, TLL commands)
├── config.toml                     # Pipeline configuration
├── project_script.sh               # Shell pipeline with FES workloads
├── chat.sh                         # Interactive chat REPL
├── voice                           # Python STT/TTS wrapper
├── setup.sh                        # Full installation script
├── create-ollama-model.sh          # Import GGUF models into Ollama
├── requirements.txt                # Python dependencies
├── workloads/                      # Function Execution Service modules
│   ├── arithmetic/                 # Math functions (add, subtract)
│   ├── system/                     # System info (CPU, memory, disk, uptime)
│   └── text/                       # Text processing functions
└── logs/
    ├── system.log                  # Pipeline execution log
    └── routing.log                 # TLL routing decisions (JSONL)
```

## Installation

### Prerequisites

- Ubuntu/Debian Linux
- Internet connection (for downloading models and packages)

### Quick Setup

Run the setup script which handles everything:

```bash
cd llm
chmod +x setup.sh
./setup.sh
```

This installs system packages, Rust, Python venv, pip dependencies, Ollama, and builds the pipeline binary.

### Manual Setup

#### 1. System Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3.12-venv portaudio19-dev ffmpeg build-essential curl -y
```

#### 2. Install Rust and Build the Pipeline

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

cd llm
cargo build --release
cp ./target/release/pipeline pipeline
```

#### 3. Python Environment

```bash
python3 -m venv env
source env/bin/activate
pip install --no-cache-dir -r requirements.txt
```

#### 4. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### 5. Download and Import the Mistral Model

The project uses **CapybaraHermes 2.5 Mistral 7B** (Q4_0 quantization). Download the GGUF file and import it into Ollama:

```bash
./create-ollama-model.sh https://huggingface.co/TheBloke/CapybaraHermes-2.5-Mistral-7B-GGUF/resolve/main/capybarahermes-2.5-mistral-7b.Q4_0.gguf?download=true
```

This downloads the model, creates an Ollama Modelfile with a conversational system prompt, registers it with Ollama, and cleans up the downloaded files.

Verify the model is available:

```bash
ollama list
# Should show: capybarahermes-2.5-mistral-7b.Q4_0:latest
```

#### 6. Start Ollama

Ollama needs to be running before using the pipeline or TLL:

```bash
ollama serve
```

Leave this running in a separate terminal or run it as a background service.

## Usage

### TLL (Routing Decisions)

Run the TLL directly with Python:

```bash
cd llm
python3 tll.py --profile Lawyer --query "My client is suing Google for damages"
python3 tll.py --profile Healthcare --query "Patient John Smith, MRN-4521, elevated glucose"
python3 tll.py --profile Journalist --query "Meeting my source at 6pm Thursday"
python3 tll.py --profile Researcher --query "Our model beats GPT-4 by 12% on MMLU"
```

Or via the Rust CLI:

```bash
./pipeline tll -q "My client is suing Google" -p Lawyer
```

TLL flags:

```
--profile, -p    Profile: Lawyer, Journalist, Healthcare, Researcher
--query, -q      The query to route
--model, -m      Ollama model (default: capybarahermes-2.5-mistral-7b.Q4_0:latest)
--raw            Print only the model response (no header/footer)
--verbose, -v    Print metadata to stderr
--log            Custom log file path (default: ./logs/routing.log)
```

### Full Pipeline (Voice)

```bash
# Run with default audio input
./pipeline

# Individual stages
./pipeline stt input.wav         # Speech-to-text
./pipeline llm "What is 2+2?"   # LLM query
./pipeline tts "Hello world"     # Text-to-speech
```

### Function Execution Pipeline

```bash
# Run with arithmetic workload
./project_script.sh -g arithmetic "What is 15 plus 27?"

# Run with system workload
./project_script.sh -g system "What is my CPU usage?"

# Interactive chat
./chat.sh
```

## Configuration

Edit `config.toml`:

```toml
python_env = "./env/bin/python3"
audio_file = "./input.wav"
llm_model = "capybarahermes-2.5-mistral-7b.Q4_0:latest"
tts_model = "af_heart"
output = "./output.wav"
stt_model = "tiny"
stt_lang = "en"
log_file = "./logs/system.log"
enable_logging = true
```


