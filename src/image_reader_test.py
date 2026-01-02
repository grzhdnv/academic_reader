from PIL import Image
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))  # GenAI client
image = Image.open(
    "/Users/mgrzhdnv/Documents/dev/academic_reader/Screenshot 2025-10-29 at 10.59.23 AM.png"
)


def read_image():
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            image,
            "You are a multilingual transcription and translation assistant specializing in historical music documents. From the given image, accurately transcribe all visible text, preserving original spelling, punctuation, and diacritics as closely as possible. Then provide a close, literal translation into English that reflects the text’s grammatical structure and tone without unnecessary modernization. Nicely format the text keeping original paragraphs structure. If the text is unclear, mark uncertain words with brackets or ellipses. Avoid summarizing or paraphrasing; your purpose is to help the user study the document in its linguistic and musical-historical context. Do not add any other text to the response, only provide transcription and translation.",
        ],
    )
    print(response.text)
    with open("test.md", "w", encoding="utf-8") as f:
        f.write(response.text)


read_image()

# Applies read_image function to all images in a directory


def process_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(
            (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")
        ):
            image_path = os.path.join(directory_path, filename)
            image = Image.open(image_path)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    image,
                    "You are a multilingual transcription and translation assistant specializing in historical music documents. From the given image, accurately transcribe all visible text, preserving original spelling, punctuation, and diacritics as closely as possible. Then provide a close, literal translation into English that reflects the text’s grammatical structure and tone without unnecessary modernization. Nicely format the text keeping original paragraphs structure. If the text is unclear, mark uncertain words with brackets or ellipses. Avoid summarizing or paraphrasing; your purpose is to help the user study the document in its linguistic and musical-historical context. Do not add any other text to the response, only provide transcription and translation.",
                ],
            )
            with open(f"{filename}.md", "w", encoding="utf-8") as f:
                f.write(response.text)


process_directory("/path/to/your/image/directory")
