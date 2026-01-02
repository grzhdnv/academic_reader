import os
from dotenv import load_dotenv
import re
import pathlib
import wave
from speed_audio import stretch_file

from google import genai
from google.genai import types

load_dotenv()  # Load environment variables from .env file

# Initialize the GenAI client with your API key from evironment variable
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# Ask user for PDF file path (drag & drop works in Mac Terminal)
user_input = input("Drag and drop your PDF file here, then press Enter: ").strip()

# Remove surrounding quotes that macOS might add
if (user_input.startswith("'") and user_input.endswith("'")) or (
    user_input.startswith('"') and user_input.endswith('"')
):
    user_input = user_input[1:-1]
filepath = pathlib.Path(user_input)
file_name = filepath.stem

# Extract the author's last name and year in parentheses
match = re.match(r"^([A-Za-z]+ ?\(\d{4}\))", file_name)
if match:
    base_name = match.group(1)
else:
    base_name = file_name  # fallback if pattern not found


(print("Generating summary..."),)
with open("prompt.txt", "r", encoding="utf-8") as prompt_file:
    prompt = prompt_file.read()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_bytes(
            data=filepath.read_bytes(),
            mime_type="application/pdf",
        ),
        prompt,
    ],
)
print("Done. Writing to file...")


# Create a directory for the output if it doesn't exist
output_dir = pathlib.Path(f"output/{base_name}")
output_dir.mkdir(parents=True, exist_ok=True)

# Save the summary to file
with open(f"{output_dir}/{base_name}.md", "w", encoding="utf-8") as f:
    f.write(response.text)  # type: ignore
    print(f"Summary saved to {base_name}.md")


## Create an audio file from the summary text
# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)


# Generate speech from text
(print("Generating audio..."),)
audio_response = client.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    contents=response.text,  # type: ignore
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Fenrir",
                )
            )
        ),
    ),
)

data = audio_response.candidates[0].content.parts[0].inline_data.data  # type: ignore

print("Done. Writing to file...")
audio_name = f"{output_dir}/{base_name}.wav"
wave_file(audio_name, data)  # Saves the file to current directory

# Speed up and trim the audio
ratio = 0.7  # Speed up by 30%
stretched_audio_name = f"{output_dir}/{base_name}_{2 - ratio}.wav"
stretch_file(audio_name, stretched_audio_name, ratio=ratio)


# Create a shorter summary
with open(f"{output_dir}/{base_name}.md", "r", encoding="utf-8") as summary_file:
    summary = summary_file.read()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Give me a paragraph summary of the following article and bullet point main arguments made:\n\n {summary}",
)
print("Done. Writing to file...")
with open(f"{output_dir}/{base_name}_short.md", "w", encoding="utf-8") as f:
    f.write(response.text)  # type: ignore
    print(f"Summary saved to {base_name}_short.md")
