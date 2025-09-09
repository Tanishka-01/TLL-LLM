#!/usr/bin/env bash
set -e

CONFIG_FILE="./config.sh"

function log() {
  if [ "$ENABLE_LOGGING" = true ]; then
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S.%3N')] $*" >> "$LOG_FILE"
  fi
}

cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null

if [ -f "$CONFIG_FILE" ]; then
  source "$CONFIG_FILE"
else
  echo "Config File Not Found: $CONFIG_FILE"
  exit 1
fi

# logging all output (stdout & stderr)
exec > >(tee -a "$LOG_FILE") 2>&1


if [ -f "$PYTHON_ENV" ]; then
  source "$PYTHON_ENV"
  log "Environment activated"
else
  echo "Python Environment Not Found: $PYTHON_ENV"
  exit 1
fi


# Parse command line arguments and expand combined single-char flags
expanded_cmds=()
for arg in "$@"; do
  if [[ $arg =~ ^-[a-zA-Z]+$ ]]; then
    # This is a combined flag like -slt, expand it and deduplicate
    seen_chars=""
    for ((i=1; i<${#arg}; i++)); do
      char="${arg:$i:1}"
      if [[ ! "$seen_chars" =~ "$char" ]]; then
        expanded_cmds+=("-${char}")
        seen_chars+="$char"
      fi
    done
  else
    # Regular argument, keep as is
    expanded_cmds+=("$arg")
  fi
done
cmds=("${expanded_cmds[@]}")


# Check for no-log flag
for arg in "$@"; do
    if [[ $arg == "-n" || $arg == "--no-log" ]]; then
        ENABLE_LOGGING=false
        log "Logging disabled"
        break
    fi
done
log "Script started with arguments: $*"


function stt() {
  log "Starting STT processing"
  ./voice stt -m $STT_MODEL -l $STT_LANG 2>> "$LOG_FILE"
  log "STT processing completed"  
}


function llm() {
  log "Starting LLM"
  #while read -r chunk; do
  #  echo "$chunk" | ollama run $LLM_MODEL
  #done
  ollama run $LLM_MODEL
  log "LLM completed"
}


function tts() {
  log "Starting TTS processing"
  ./voice tts -v $TTS_MODEL -o $OUTPUT 2>> "$LOG_FILE"
  log "TTS processing completed"
}


function help-message() {
  log "Displaying help message and exiting"

  echo -e "Usage: $0 [-s] [-l] [-t] [-h]\n"
  echo "optional arguments:"
  echo -e "  -s, --stt\t Run speech-to-text only"
  echo -e "  -l, --llm\t Run up to LLM processing"
  echo -e "  -t, --tts\t Run full pipeline including TTS"
  echo -e "  -n, --no-log\t Disables logging\n"
  echo -e "  -h, --help\t show this help message and exit\n"
  log "--------------------------------------------------------------------"
}


# Build the pipeline based on arguments
if [ ${#cmds[@]} -eq 0 ]; then
  log "No args provided, running full pipeline"
  stt | llm | tts
else
  # Build pipeline based on provided arguments
  pipeline_parts=()
  
  for c in "${cmds[@]}"; do
    case $c in
      "-s" | "--stt") pipeline_parts+=("stt");;
      "-l" | "--llm") pipeline_parts+=("llm");;
      "-t" | "--tts") pipeline_parts+=("tts");;
      "-h" | "--help")
        help-message
        exit 0
        ;;
      *)
        echo -e "Unknown argument: $c\n"
        log "User input Unknown argument: $c"
        help-message
        exit 1
        ;;
    esac
  done
  

  # Execute the built pipeline
  if [ ${#pipeline_parts[@]} -gt 0 ]; then
    log "Building pipeline with parts: ${pipeline_parts[*]}"
    cmd=""
    
    if [ ${#pipeline_parts[@]} -eq 1 ]; then 
      cmd="${pipeline_parts[0]}"
    else
      # Add each function in sequence
      for func in "${pipeline_parts[@]}"; do
        cmd="$cmd | $func"
      done
    fi
    
    log "Executing pipeline: $cmd"
    eval "cmd"
  fi
fi
log "Script execution completed\n--------------------------------------------------------------------"
