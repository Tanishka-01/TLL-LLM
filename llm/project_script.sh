#!/usr/bin/env bash
#
# project_script.sh - Main pipeline
#
# Usage:
#   ./project_script.sh                        # Interactive
#   ./project_script.sh "your question"        # Direct prompt
#   ./project_script.sh -g arithmetic "q"      # Use specific function group
#
# Options:
#   -g, --group        Function group (system, arithmetic, text)
#   -h, --help         Show this help
#

project_path=$(dirname "$(readlink -f $0)")
cd $project_path

# Defaults
FUNCTION_GROUP="system"
PROMPT_ID=1

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -g|--group)
            FUNCTION_GROUP="$2"
            shift 2
            ;;
        -h|--help)
            head -n 14 "$0" | tail -n 12
            exit 0
            ;;
        *)
            OG_PROMPT="$1"
            shift
            ;;
    esac
done

WORKLOAD_DIR="./workloads"
AI_PIPELINE_BIN="./pipeline"
source env/bin/activate

FES_BIN="python $WORKLOAD_DIR/$FUNCTION_GROUP/FES.py"

# If no prompt provided, read from file
if [ -z "$OG_PROMPT" ]; then
    if [ -f "$WORKLOAD_DIR/$FUNCTION_GROUP/prompts/$PROMPT_ID" ]; then
        OG_PROMPT=$(cat "$WORKLOAD_DIR/$FUNCTION_GROUP/prompts/$PROMPT_ID")
    else
        echo "Enter your prompt:"
        read -r OG_PROMPT
    fi
fi

if [ -z "$OG_PROMPT" ]; then
    echo "Error: No prompt provided."
    exit 1
fi

FES_SPEC=$(cat "$WORKLOAD_DIR/$FUNCTION_GROUP/fes_functions.txt")
FIRST_PROMPT=$(cat "$WORKLOAD_DIR/first_base.txt")
SECONDARY_PROMPT=$(cat "$WORKLOAD_DIR/secondary_base.txt")

LOGS_DIR="./logs"
mkdir -p "$LOGS_DIR"

# --- STARTING PIPELINE ---
uuid_prompt="$(date +%s)_$(($RANDOM % 1000))"

echo ""
echo "=========================================="
echo "  LLM PIPELINE - Function Execution"
echo "=========================================="
echo "  Function Group: $FUNCTION_GROUP"
echo "  Run ID: $uuid_prompt"
echo "=========================================="
echo ""

# First prompt
prompt_file_name="$LOGS_DIR/p$uuid_prompt"
touch $prompt_file_name
echo -e "$OG_PROMPT\n" >> $prompt_file_name
echo -e "$FES_SPEC\n" >> $prompt_file_name
echo "$FIRST_PROMPT" >> $prompt_file_name

# Run LLM
llm_output_file=$LOGS_DIR/l$uuid_prompt
touch $llm_output_file

echo ">>> Step 1: Running LLM inference..."
$AI_PIPELINE_BIN llm "$(cat $prompt_file_name)" >> $llm_output_file

# Run FES
echo ">>> Step 2: Executing functions..."
functions_output_file=$LOGS_DIR/f$uuid_prompt
touch $functions_output_file
$FES_BIN $llm_output_file >> $functions_output_file

# Second prompt
prompt2_file_name="$LOGS_DIR/s$uuid_prompt"
touch $prompt2_file_name
echo -e "$OG_PROMPT\n" >> $prompt2_file_name
echo -e "$(cat $functions_output_file)\n" >> $prompt2_file_name
echo "$SECONDARY_PROMPT" >> $prompt2_file_name

# Final output
echo ">>> Step 3: Generating final response..."
final_output=$($AI_PIPELINE_BIN llm "$(cat $prompt2_file_name)")

echo ""
echo "=========================================="
echo "  RESPONSE"
echo "=========================================="
echo "$final_output"
echo "=========================================="

# Text-to-speech
echo ""
echo ">>> Step 4: Converting to speech..."
$AI_PIPELINE_BIN tts "$final_output"
aplay ./misc/llm-output.wav 2>/dev/null || true

echo ""
echo "Logs saved to $LOGS_DIR/ (p$uuid_prompt, l$uuid_prompt, f$uuid_prompt, s$uuid_prompt)"
