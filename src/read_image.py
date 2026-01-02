import os
import re

from dotenv import load_dotenv

from PIL import Image
from google import genai

load_dotenv()  # Load environment variables from .env file

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))  # GenAI client

user_input = input("Drag and drop your PDF file here, then press Enter: ").strip()

# Remove surrounding quotes that macOS might add
if (user_input.startswith("'") and user_input.endswith("'")) or (
    user_input.startswith('"') and user_input.endswith('"')
):
    user_input = user_input[1:-1]


def read_image(image_path, filename):
    # Exception handling for 503 errors can be added here if needed
    try:
        image = Image.open(image_path)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                image,
                "You are a multilingual transcription and translation assistant specializing in historical music documents. From the given image, accurately transcribe text, preserving original paragraphs, spelling, punctuation, and diacritics as closely as possible. Then provide a close, literal translation into English that reflects the grammatical structure and tone of the text without unnecessary modernization. If the text is unclear, mark uncertain words with brackets or ellipses. Avoid summarizing or paraphrasing; your purpose is to help the user study the document in its linguistic and musical-historical context. Do not add any other text to the response, only provide transcription and translation.",
            ],
        )
        # keep only the final 6 digits from the input filename (e.g. "Screenshot ... 114435.png" -> "114435.md")
        stem = os.path.splitext(filename)[0]
        m = re.search(r"(\d{6})$", stem)
        out_name = m.group(1) if m else stem
        with open(f"{out_name}.md", "w", encoding="utf-8") as f:
            f.write(response.text)  # type: ignore
    except Exception as e:  # Catch all exceptions for simplicity
        print(
            f"{e}. Service is currently unavailable. Please try again later. Last attempted file: {image_path}"
        )


# Applies read_image function to all images in a directory
def process_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            print(f"Processing file: {filename}")
            image_path = os.path.join(directory_path, filename)
            read_image(image_path, filename)


process_directory(user_input)
