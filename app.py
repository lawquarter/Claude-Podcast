import os
from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
from io import BytesIO
from anthropic import Anthropic
from pydub import AudioSegment
import uuid
from elevenlabs.client import ElevenLabs
from Joking import random_joke

app = Flask(__name__)

# Ensure FFmpeg is in your PATH or specify the full path
AudioSegment.converter = "ffmpeg"
AudioSegment.ffmpeg = "ffmpeg"
AudioSegment.ffprobe = "ffprobe"

load_dotenv()

# Get API keys from environment variables
XI_API_KEY = os.getenv("XI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Check if the variables are set
if not XI_API_KEY:
    raise ValueError("XI_API_KEY is not set in the environment variables")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is not set in the environment variables")
elevenlabs = ElevenLabs(api_key=os.getenv(XI_API_KEY))
# Create a directory to store audio files
AUDIO_DIR = os.path.join(app.root_path, 'audio_files')
os.makedirs(AUDIO_DIR, exist_ok=True)

# Path to the intro file
INTRO_FILE = os.path.join(app.root_path, '0630.MP3')
Joke = random_joke()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    article = request.json['article']
    style = request.json['style']
    try:
        if style == 'podcast':
            script = generate_podcast_script(article)
            return jsonify({'script': script})
        elif style == 'news':
            news_article = generate_news_article(article)
            return jsonify({'article': news_article})
        else:
            return jsonify({'error': 'Invalid style selected'}), 400
    except Exception as e:
        app.logger.error(f"Error in conversion process: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate-audio', methods=['POST'])
def generate_audio():
    script = request.json['script']
    try:
        audio_data = convert_to_speech(script)
        audio_filename = merge_audio_segments(audio_data)
        return jsonify({'audio_filename': audio_filename})
    except Exception as e:
        app.logger.error(f"Error in audio generation process: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(AUDIO_DIR, filename, as_attachment=True)

def generate_podcast_script(article):
    app.logger.info("Generating podcast script")
    anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
    try:
        response = anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": f"""Generate a podcast script for two speakers based on the following article. Make it engaging and conversational and detailed and interesting. Ensure the questions build on the answers and talk about personal insights. Speaker 1 should call Speaker 2 Anabelle and Speaker 2 should call Speaker 1 Max. Speaker 1 should ask questions and Anabelle (speaker 2) is the expert explaining. Do not be complementary of one another. The questions should be probing and ask for examples. Do not instruct the speakers to laugh or chuckle as they will simply read exactly what you tell them to. Just have the lines they are to speak. Use 'Speaker 1:' and 'Speaker 2:' to distinguish between the speakers. Each speaker's line should start on a new line and if the speaker has something to say that covers more that one line each of their lines should start with the identifier 'Speaker 1:' or 'Speaker 2:'. Where there is a list of items just include it in the same line for the speaker. 
                    From time to time (maximum 2 times), add a sound effect instruction using the format 'Sound effect:' followed by a brief description of the sound. The sound effect should be no more than 3 seconds long. For example:

                    Sound effect: A soft whoosh

                    Here's the article:

                    {article}"""
                }
            ]
        )
        
        script = response.content[0].text
        app.logger.info(f"Podcast script generated. Length: {len(script)}")
        print("Generated Script:")
        print(script)  # Print the generated script
        return script
    except Exception as e:
        app.logger.error(f"Anthropic API error: {str(e)}")
        raise Exception(f"Anthropic API error: {str(e)}")

def generate_sound_effect(text: str) -> AudioSegment:
    app.logger.info(f"Generating sound effect: {text}")
    try:
        response = requests.post(
            "https://api.elevenlabs.io/v1/sound-generation",
            headers={
                "Accept": "audio/mpeg",
                "xi-api-key": XI_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "duration_seconds": 3,  # Maximum duration of 3 seconds
                "prompt_influence": 0.5  # You can adjust this value as needed
            },
        )

        if response.status_code != 200:
            app.logger.error(f"ElevenLabs API error for sound effect: {response.status_code} - {response.text}")
            raise Exception(f"ElevenLabs API error for sound effect: {response.status_code}")

        sound_effect = AudioSegment.from_mp3(BytesIO(response.content))
        
        app.logger.info(f"Sound effect generated successfully")
        return sound_effect
    except Exception as e:
        app.logger.error(f"Error generating sound effect: {str(e)}")
        raise

def generate_news_article(article):
    app.logger.info("Generating news article")
    anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
    try:
        response = anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": f"Rewrite the following article into a news story in a clear, concise newsreader style. There should be two newsreaders. Speaker 1 is Max and Speaker 2 Anabelle. The tone should be objective and professional, suitable for a general audience.  Use 'Speaker 1:' and 'Speaker 2:' to distinguish between the speakers. Each speaker's line should start on a new line. Include relevant facts and potential impacts where appropriate:\n\n{article}"
                }
            ]
        )
        
        news_article = response.content[0].text
        app.logger.info(f"News article generated. Length: {len(news_article)}")
        return news_article
    except Exception as e:
        app.logger.error(f"Anthropic API error: {str(e)}")
        raise Exception(f"Anthropic API error: {str(e)}")
    
def convert_to_speech(script):
    app.logger.info("Converting script to speech")
    lines = script.split('\n')
    audio_data = []

    for line in lines:
        if line.startswith("Speaker 1:") or line.startswith("Speaker 2:"):
            speaker, text = line.split(": ", 1)
            voice_id = 'L0Dsvb3SLTyegXwtm47J' if speaker == "Speaker 1" else 'gDnGxUcsitTxRiGHr904' 

            try:
                response = requests.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream",
                    headers={
                        "Accept": "audio/mpeg",
                        "xi-api-key": XI_API_KEY,
                        "Content-Type": "application/json",
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_monolingual_v1",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75,
                        },
                    },
                )

                if response.status_code != 200:
                    app.logger.error(f"ElevenLabs API error for {speaker}: {response.status_code} - {response.text}")
                    raise Exception(f"ElevenLabs API error for {speaker}: {response.status_code}")

                audio_segment = AudioSegment.from_mp3(BytesIO(response.content))
                audio_data.append(audio_segment)

            except requests.RequestException as e:
                app.logger.error(f"Request error for {speaker}: {str(e)}")
                raise Exception(f"Request error for {speaker}: {str(e)}")

        elif line.startswith("Sound effect:"):
            _, effect_description = line.split(": ", 1)
            try:
                sound_effect = generate_sound_effect(effect_description)
                audio_data.append(sound_effect)
                app.logger.info(f"Generated sound effect: {effect_description}")
            except Exception as e:
                app.logger.error(f"Error generating sound effect: {str(e)}")
                # Continue with the script even if sound effect generation fails

    app.logger.info(f"Speech conversion complete. Number of audio segments: {len(audio_data)}")
    return audio_data

def merge_audio_segments(audio_data):
    app.logger.info("Merging audio segments")
    
    # Load the intro file
    try:
        intro_audio = AudioSegment.from_mp3(INTRO_FILE)
        app.logger.info(f"Loaded intro file: {INTRO_FILE}")
    except Exception as e:
        app.logger.error(f"Error loading intro file: {str(e)}")
        intro_audio = AudioSegment.empty()  # Use an empty segment if intro file can't be loaded

    # Start with the intro
    merged_audio = intro_audio

    for audio_segment in audio_data:
        merged_audio += audio_segment

    # Generate a unique filename
    filename = f"podcast_{uuid.uuid4()}.wav"
    file_path = os.path.join(AUDIO_DIR, filename)

    # Save the merged audio
    merged_audio.export(file_path, format="wav")
    app.logger.info(f"Merged audio saved to {file_path}")

    return filename

if __name__ == '__main__':
    app.run(debug=True)