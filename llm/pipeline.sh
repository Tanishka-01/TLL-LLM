#!/usr/bin/env bash
set -e

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


# TODO might change in future
#SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null
source ./python-env/bin/activate



# Pipeline components as functions
function input_source() {
  # TODO: change in future so script doesn't call hardcoded file
  ffmpeg -i dbd_debate.mp4 -f s16le -acodec pcm_s16le -ac 1 -ar 16000 - 2>/dev/null
}


function stt() {
  #python3 transcribe.py 2>/dev/null | \
  #python3 ./transcribe.py | \
  python3 ./transcribe.py
}


function llm() {
  #while read -r chunk; do
    #echo "$chunk" | ollama run convo-ai
  #done
  while read -r chunk; do
    echo "$chunk" | cat
  done
}


function tts() {
  # TODO: Implement TTS functionality
  while read -r chunk; do
    echo "TTS would process: $chunk"
  done
}


function help-message() {
  echo -e "Usage: $0 [-s] [-l] [-t] [-h]\n"
  echo "optional arguments:"
  echo -e "  -h, --help\t show this help message and exit"
  echo -e "  -s, --stt\t Run speech-to-text only"
  echo -e "  -l, --llm\t Run up to LLM processing"
  echo -e "  -t, --tts\t Run full pipeline including TTS\n"
}





# Build the pipeline based on arguments
if [ ${#cmds[@]} -eq 0 ]; then
  # No arguments - run full pipeline: source | stt | llm | tts
  echo "no args provided, running full pipeline"
  input_source | stt | llm | tts
else
  # Build pipeline based on provided arguments
  pipeline=""
  
  for c in "${cmds[@]}"; do
    case $c in
      "-s" | "--stt")
        if [ -z "$pipeline" ]; then
          pipeline="input_source | stt"
        else
          pipeline="$pipeline | stt"
        fi
        ;;

      "-l" | "--llm")
        # TODO: fix so that pipeline only runs llm in future
        if [ -z "$pipeline" ]; then
          pipeline="input_source | stt | llm"
        else
          pipeline="$pipeline | llm"
        fi
        ;;

      "-t" | "--tts")
        # TODO: fix so that pipeline only runs tts in future
        if [ -z "$pipeline" ]; then
          pipeline="input_source | stt | llm | tts"
        else
          pipeline="$pipeline | tts"
        fi
        ;;

      "-h" | "--help")
        help-message
        exit 0
        ;;

      *)
        echo -e "Unknown argument: $c\n"
        help-message
        exit 1
        ;;
        
    esac
  done
  
  # Execute the built pipeline
  if [ -n "$pipeline" ]; then
    eval "$pipeline"
  fi
fi
