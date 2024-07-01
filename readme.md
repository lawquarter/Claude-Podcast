# Claude Opus Podcast Generator

## Overview

The Claude Opus Podcast Generator is a Flask-based web application that leverages artificial intelligence to create podcast scripts and news articles from user-provided content. It utilizes the Anthropic API for text generation and the ElevenLabs API for text-to-speech conversion, allowing users to generate both written and audio content.

## Features

- Generate podcast scripts from input articles
- Create news articles from input content
- Convert generated scripts to audio using text-to-speech technology
- Edit generated scripts before audio conversion
- Download generated audio files
- Incorporate sound effects into podcast audio

## Prerequisites

- Python 3.7+
- FFmpeg (ensure it's in your system PATH or specify the full path in the code)
- API keys for Anthropic and ElevenLabs

## Installation

1. Clone the repository:
   ```
   git clone this repo 
   cd ai-content-generator
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   - Create a `.env` file in the project root
   - Add your API keys:
     ```
     XI_API_KEY=your_elevenlabs_api_key
     ANTHROPIC_API_KEY=your_anthropic_api_key
     ```

## Configuration

- Ensure FFmpeg is installed and accessible in your system PATH, or update the following lines in `app.py` with the full path:
  ```python
  AudioSegment.converter = "path/to/ffmpeg"
  AudioSegment.ffmpeg = "path/to/ffmpeg"
  AudioSegment.ffprobe = "path/to/ffprobe"
  ```

- The application uses an intro audio file. Ensure `0630.MP3` is present in the application root directory, or update the `INTRO_FILE` path in `app.py`.

## Usage

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open a web browser and navigate to `http://localhost:5000`.

3. Use the web interface to:
   - Input an article
   - Choose between podcast or news article generation
   - Generate content
   - For podcasts:
     - Edit the generated script if desired
     - Generate audio from the script
   - Download the generated audio file

## API Endpoints

- `/convert` (POST): Convert input article to podcast script or news article
- `/generate-audio` (POST): Generate audio from a provided script
- `/download/<filename>` (GET): Download generated audio files

## File Structure

- `app.py`: Main Flask application file
- `templates/index.html`: HTML template for the web interface
- `audio_files/`: Directory where generated audio files are stored
- `0630.MP3`: Intro audio file for podcasts

## Error Handling

The application includes error handling for API requests and file operations. Check the application logs for detailed error messages in case of issues.

## Customization

- Modify the `generate_podcast_script` and `generate_news_article` functions in `app.py` to adjust the prompts sent to the Anthropic API.
- Adjust voice settings and model parameters in the `convert_to_speech` function to change the audio output characteristics.

## Security Notes

- Keep your API keys confidential and do not expose them in public repositories.
- Implement proper input validation and sanitization for production use.
- Consider implementing user authentication for a public-facing application.

## Contributing

Contributions to improve the AI Content Generator are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a pull request

## License

GNU General Public License v3.0

## Acknowledgments

- Anthropic for their powerful language model API
- ElevenLabs for their text-to-speech technology
- Flask community for the web framework

## Support

For support, please open an issue in the GitHub repository. 

