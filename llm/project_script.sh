#!/usr/bin/env bash

#set -e 

project_path=$(dirname "$(readlink -f $0)")
cd $project_path

# function exec service (FES)

# these are to be changed based off user input
prompt_id=1 
#function_group="bird_net"
function_group="arithmetic"





WORKLOAD_DIR="./workloads"
AI_PIPELINE_BIN="./pipeline" 
source env/bin/activate
FES_BIN="$WORKLOAD_DIR/$WORKLOAD_DIR/FES.sh" # needs to be implemented for each type of function I believe


# user prompt for each function
OG_PROMPT=$(cat "$WORKLOAD_DIR/$function_group/prompts/$prompt_id")

FES_SPEC=$(cat "$WORKLOAD_DIR/$function_group/fes_functions.txt") # list of tools
FIRST_PROMPT=$(cat "$WORKLOAD_DIR/first_base.txt") # how to format tools to use them

SECONDARY_PROMPT=$(cat "$WORKLOAD_DIR/secondary_base.txt") # needs to be made

#DEBUG_PROMPTS="$WORKLOAD_DIR/prompts"
LOGS_DIR="./logs"

# --- STARTING PIPELINE ---
# creates file that has the init prompt for the llm
uuid_prompt="$(date +%s)_$(($RANDOM % 1000))"

prompt_file_name="$LOGS_DIR/p$uuid_prompt" #p is for primary prompt
touch $prompt_file_name

echo -e "$OG_PROMPT\n" >> $prompt_file_name
echo -e "$FES_SPEC\n" >> $prompt_file_name
echo "$FIRST_PROMPT" >> $prompt_file_name


# runs llm with prompt and finds what functions it needs, dumps output in logs
llm_output_file=$LOGS_DIR/l$uuid_prompt
touch $llm_output_file # l is for llm
$AI_PIPELINE_BIN llm "$(cat $prompt_file_name)" >> $llm_output_file

# Searches for requested functions and runs them
functions_output_file=$LOGS_DIR/f$uuid_prompt
touch $functions_output_file # f is for the function output
### TODO need to grep through file output and then call the function through flask api
$FES_BIN $llm_output_file >> $functions_output_file 

## calls llm again with same prompt but this time with the output of the function calls
prompt2_file_name="$LOGS_DIR/s$uuid_prompt" #s is for secondary prompt
touch $prompt2_file_name

echo -e "$OG_PROMPT\n" >> $prompt2_file_name
echo -e "$(cat $functions_output_file)\n" >> $prompt2_file_name  
echo "$SECONDARY_PROMPT" >> $prompt2_file_name

#echo -e "\n-----second AI prompt-----\n" >> $llm_output_file
#$AI_PIPELINE_BIN llm $prompt2_file_name >> $llm_output_file 

#$AI_PIPELINE_BIN llm $prompt2_file_name > $llm_output_file 
$AI_PIPELINE_BIN llm $prompt2_file_name

#$AI_PIPELINE_BIN tts $(cat $llm_output_file) 
#final output TODO either add a new output file option to tts or make -c config string as arg

