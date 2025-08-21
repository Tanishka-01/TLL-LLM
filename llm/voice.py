#!/usr/bin/env python3

import os
os.environ['MKL_THREADING_LAYER'] = 'GNU'
os.environ['OMP_NUM_THREADS'] = '1'

import numpy as np
import os
import threading
import queue
import time
import logging
from constants import data_dir, cache_dir, STT_MODELS, SPEACH_RECOGNITION_LANGUAGES, TTS_VOICES
import torch

torch.backends.nnpack.enabled = False
logger = logging.getLogger(__name__)

libraries = {
    'kokoro': None,
    'sounddevice': None,
    'whisper': None,
    'pyaudio': None
}

# reuse if running 
loaded_whisper_models = {}
tts_engine = None
tts_engine_language = None

def preload_heavy_libraries():
    global libraries
    for library_name in libraries:
        if libraries.get(library_name) is None:
            try:
                import importlib.util
                spec = importlib.util.find_spec(library_name)
                if spec is not None:
                    # Use importlib.import_module instead of importlib.util.import_module
                    libraries[library_name] = importlib.import_module(library_name)
                    print(f"Successfully loaded {library_name}")
                else:
                    print(f"Module {library_name} not found")
            except Exception as e:
                print(f"Failed to load {library_name}: {e}")



# shorten the number or libaries needed for this function, so far there's 4
# give option to swtich to different voices
"""
def run_tts(text, voice=None, speed=1.2, output_file=None):
    import warnings
    from constants import TTS_VOICES
    warnings.filterwarnings('ignore')
    valid_voice_codes = list(TTS_VOICES.values())

    global tts_engine, tts_engine_language

    if voice is None:
        voice = 'af_heart'  # Default voice
    elif voice not in valid_voice_codes:
        print(f"Warning: Invalid voice '{voice}', using default 'af_heart'")
        voice = 'af_heart'

    # Generate TTS_ENGINE if needed
    if not tts_engine or tts_engine_language != voice[0]:
        try:
            if libraries.get('kokoro') is None:
                raise RuntimeError("Kokoro library not available")
            tts_engine = libraries.get('kokoro').KPipeline(lang_code=voice[0], repo_id='hexgrad/Kokoro-82M')
            tts_engine_language = voice[0]
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            raise RuntimeError("Failed to initialize TTS engine.") from e

    play_queue = queue.Queue()

    
    def play_audio_queue():
        audio_frames = []
        while True:
            audio = play_queue.get()
            if audio is None:
                break
            audio_frames.append(audio)
        try:
            if output_file:
                # Save to file instead of playing
                with open(output_file, 'wb') as f:
                    for frame in audio_frames:
                        f.write(frame.tobytes())
                print(f"Audio saved to {output_file}")
            else:
                if audio_frames:  # Only play if we have audio frames
                    try:
                        combined_audio = np.concatenate(audio_frames)
                        combined_audio = combined_audio.astype(np.float32) / 32768.0
                        libraries.get('sounddevice').play(combined_audio, samplerate=22050)
                        libraries.get('sounddevice').wait()
                    except Exception as e:
                        print(f"Error playing audio: {e}")
        except Exception as e:
            print(f"Error in audio playback: {e}")

    play_thread = threading.Thread(target=play_audio_queue, daemon=True)
    play_thread.start()
    

    try:
        generator = tts_engine(text, voice=voice, speed=speed, split_pattern=r'\n+')
        for gs, ps, audio in generator:
            play_queue.put(audio)

    except Exception as e:
        logger.error(f"Error during TTS generation: {e}")
        raise RuntimeError("Failed to generate speech.") from e

    
    play_queue.put(None)
    play_thread.join()
"""

def run_tts(text, voice=None, speed=1.2, output_file=None):
    import warnings
    from constants import TTS_VOICES
    warnings.filterwarnings('ignore')
    valid_voice_codes = list(TTS_VOICES.values())

    # Validate voice parameter
    if voice is None:
        voice = 'af_heart'  # Default voice
    elif voice not in valid_voice_codes:
        print(f"Warning: Invalid voice '{voice}', using default 'af_heart'")
        voice = 'af_heart'

    try:
        from kokoro import KPipeline
        
        # Create pipeline
        pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
        
        # Generate speech
        generator = pipeline(text, voice=voice, speed=speed)
        
        # Collect audio chunks
        audio_chunks = []
        chunk_count = 0
        
        for i, (gs, ps, audio) in enumerate(generator):
            audio_chunks.append(audio)
            chunk_count += 1
        
        if chunk_count > 0 and audio_chunks:
            import soundfile as sf
            # Combine all audio chunks
            combined_audio = np.concatenate(audio_chunks)
            
            if output_file:
                # Save to file
                sf.write(output_file, combined_audio, 24000)
                print(f"Audio saved to {output_file}")
            else:
                # Play audio
                import sounddevice as sd
                sd.play(combined_audio, samplerate=24000)
                sd.wait()
                print("Audio played successfully")
        else:
            print("No audio generated")
            
    except Exception as e:
        logger.error(f"Error during TTS generation: {e}")
        import traceback
        traceback.print_exc()
        raise RuntimeError("Failed to generate speech.") from e


def run_stt(model_name, language, input_file):
    global loaded_whisper_models

    # Check if model exists
    model_path = os.path.join(data_dir, 'whisper', f'{model_name}.pt')
    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"Model {model_name} is not downloaded. Please download it first.")

    try:
        if not loaded_whisper_models.get(model_name):
            loaded_whisper_models[model_name] = libraries.get('whisper').load_model(
                model_name, 
                download_root=os.path.join(data_dir, 'whisper')
            )
    except Exception as e:
        logger.error(e)
        raise RuntimeError("Failed to load speech recognition model.") from e

    try:
        result = loaded_whisper_models.get(model_name).transcribe(input_file, word_timestamps=False)
        segments = result['segments']
        paragraphs = []
        current_para = []

        for seg in segments:
            current_para.append(seg['text'].strip())
            if len(current_para) >= 5:  # Group every 5 sentences
                paragraphs.append(' '.join(current_para))
                current_para = []
        
        if current_para:
            paragraphs.append(' '.join(current_para))

        return '\n\n'.join(paragraphs)
    except Exception as e:
        logger.error(e)
        raise RuntimeError("Failed to transcribe audio file.") from e



def download_model(model_name):
    try:
        # Create directories
        os.makedirs(os.path.join(data_dir, 'whisper'), exist_ok=True)
        
        model = libraries.get('whisper').load_model(
            model_name, 
            download_root=os.path.join(data_dir, 'whisper')
        )
        print(f"Model {model_name} downloaded successfully.")
    except Exception as e:
        logger.error(e)
        raise RuntimeError(f"Failed to download model {model_name}.") from e







if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Text-to-Speech and Speech-to-Text CLI Tool")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # TTS Parser
    tts_parser = subparsers.add_parser('tts', help='Convert text to speech')
    tts_parser.add_argument('-v', '--voice', default='af_heart', help='Voice model (default: english)')
    tts_parser.add_argument('-o', '--output-file', help='Output audio file path')
    tts_parser.add_argument('-s', '--speed', type=float, default=1.2, help='Speech speed (default: 1.2)')
    tts_parser.add_argument('text', nargs='*', help='Text to convert to speech')

    # STT Parser
    stt_parser = subparsers.add_parser('stt', help='Convert speech to text')
    stt_parser.add_argument('-m', '--model', required=True, choices=list(STT_MODELS.keys()), help='Speech recognition model')
    stt_parser.add_argument('-l', '--language', default='en', choices=list(SPEACH_RECOGNITION_LANGUAGES.keys()), help='Language for speech recognition (default: en)')
    stt_parser.add_argument('input_file', help='Input audio file path')

    # Download Parser
    download_parser = subparsers.add_parser('download', help='Download a speech recognition model')
    download_parser.add_argument('-m', '--model', required=True, choices=list(STT_MODELS.keys()), help='Model to download')

    # Check if no arguments provided or help message to avoid unnessasary compute
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    elif sys.argv[1] == '-h' or sys.argv[1] == '--help':
        parser.print_help()
        sys.exit(0)

    # might not need, 
    # or change so that we only load the libraries we need
    # for now keep to save on time
    preload_heavy_libraries()



    args = parser.parse_args()

    if args.command == 'tts':
        if args.text:
            text = ' '.join(args.text)
        else:
            try:
                # Try to read from stdin, but don't hang indefinitely
                # Read all input or timeout after a short time
                import select
                import sys
                
                if not sys.stdin.isatty():  # If not interactive terminal
                    text = sys.stdin.read().strip()
                else:
                    # Interactive terminal - require explicit text or exit
                    print("No text provided for TTS", file=sys.stderr)
                    sys.exit(1)
            except Exception:
                # Fallback
                if not sys.stdin.isatty():
                    text = sys.stdin.read().strip()
                else:
                    print("No text provided for TTS", file=sys.stderr)
                    sys.exit(1)
        if not text:
            print("No text provided for TTS", file=sys.stderr)
            sys.exit(1)
        
        run_tts(text, voice=args.voice, speed=args.speed, output_file=args.output_file)

    elif args.command == 'stt':
        result = run_stt(args.model, args.language, args.input_file)
        print(result)

    elif args.command == 'download':
        download_model(args.model)

