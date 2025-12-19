#!/usr/bin/env bash

set -e # exit if errors

AI_PIPELINE_BIN="./llm/pipeline"
MCP_SERVER_BIN="./mcp-server/target/debug/pipeline-mcp???" # this doesn't compile

og_prompt="prompt0.txt"
API_SPEC_FILE="API_SPEC_FILE.txt" # list of tools from mcp server
FORMAT_OUTPUT_FOR_CMDS="HOW_TO_FORMAT_OUTPUT_FOR_CMDS.txt" # how to format tools to use them

#input should be sound file like 'file.wav'

#$AI_PIPELINE_BIN stt $1 #| \
$AI_PIPELINE_BIN stt "../llm/things/space.wav" #| \ for testing





#$AI_PIPELINE_BIN llm "First list all of the tools to invoke" <<< "$og_prompt $API_SPEC_FILE $FORMAT_OUTPUT_FOR_CMDS" | \
#$MCP_SERVER_BIN -o CMD_OUTPUT | \ # need to make 'pipeline-mcp' and 'CMD_OUTPUT' is confusing
#$AI_PIPELINE_BIN llm $og_prompt CMD_OUTPUT | \
#$AI_PIPELINE_BIN tts #final output TODO either add a new output file option to tts or make -c config string as arg
