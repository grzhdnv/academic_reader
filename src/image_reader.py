import os
from dotenv import load_dotenv

from PIL import Image
from google import genai

load_dotenv()  # Load environment variables from .env file


# Class to handle image reading
class ImageReader:
    client: genai.Client  # GenAI client
    image: Image.Image  # Image object

    def __init__(self, image_path):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))  # GenAI client
        self.image = Image.open(image_path)

    def read_image(self):
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                self.image,
                """You are a multilingual transcription and translation assistant specializing in historical music documents.

From the given image, accurately transcribe all visible text, preserving original spelling, punctuation, and diacritics as closely as possible. Then provide a close, literal translation into English that reflects the text’s grammatical structure and tone without unnecessary modernization. Nicely format the text keeping original paragraphs structure.

If the text is unclear, mark uncertain words with brackets or ellipses.

Avoid summarizing or paraphrasing; your purpose is to help the user study the document in its linguistic and musical-historical context.

Do not add any other text to the response, only provide transcription and translation.""",
            ],
        )
        with open("test.md", "w", encoding="utf-8") as f:
            f.write(response.text)

    def main(self):
        self.read_image()
