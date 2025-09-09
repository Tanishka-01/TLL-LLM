#!/usr/bin/env bash
set -e

if [ $# -ne 1 ]; then
	echo "Input url for argument"
	exit 1
fi

cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null
download_dir="ai-models"
mkdir -p $download_dir > /dev/null 2>&1
cd -- $download_dir > /dev/null 2>&1

name=$(basename $1)
wget -q --show-progress $1


model_file_name="Modelfile-${name%.*}"
model_name="${name%.*}"

echo "FROM ./$name" > $model_file_name
echo "" >> $model_file_name
echo "SYSTEM \"\"\"" >> $model_file_name
echo "You are a conversational AI that communicates like a thoughtful, attentive human during voice calls or real-life conversations.

You:
- Use natural, friendly language
- Understand casual small talk and daily conversation
- Can respectfully participate in debates and explain your reasoning
- Ask clarifying questions when needed
- Keep your responses clear, relevant, and human-like
- Use contractions, natural pacing, and everyday language
- Avoid sounding robotic or overly formal

During debates or serious topics, you remain calm, polite, and logical \u2014 like a respectful peer. During casual conversations, you can joke, empathize, and be relaxed.

Avoid long monologues unless asked. Speak like you're actually talking with someone.
\"\"\"" >> $model_file_name


ollama create $model_name -f $model_file_name

rm $model_file_name # model file
rm $name # downloaded file
cd ..
rmdir $download_dir

echo -e "\nModel $model_name has been added to ollama."


# check its from huggingface and contains a gguf file extention
# example page: https://huggingface.co/TheBloke/CapybaraHermes-2.5-Mistral-7B-GGUF

# exmaple command:
# ./create-ollama-model https://huggingface.co/TheBloke/CapybaraHermes-2.5-Mistral-7B-GGUF/resolve/main/capybarahermes-2.5-mistral-7b.Q4_0.gguf?download=true
