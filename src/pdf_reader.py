import os
import pathlib

from dotenv import load_dotenv

from google import genai
from google.genai import types

load_dotenv()  # Load environment variables from .env file


# Class to handle pdf reading
class Readr:
    """Class to process pdf and md documents with Gemini API.

    Attributes:
        client (genai.Client): GenAI client initialized with API key.
    """

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))  # GenAI client

    @staticmethod
    def transcribe_pdf(
        file_path,
        prompt_file="./prompts/transcribe_pdf.md",
        model="gemini-3-flash-preview",
        output_dir="./out/",
    ):
        """
        Transcribe PDF to markdown using Gemini.
        """

        with open(prompt_file, "r", encoding="utf-8") as p:
            prompt = p.read()
        print("Processing PDF to markdown...")

        # Generate content using Gemini API
        response = Readr.client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(
                    data=pathlib.Path(file_path).read_bytes(),
                    mime_type="application/pdf",
                ),
                prompt,
            ],
        )

        if response.text is None:
            print("Error: Response text is None.")
            print("Full response:", response)
            return

        # create a subfolder for output based on input file name
        out_dir = pathlib.Path(output_dir) / pathlib.Path(file_path).stem
        out_dir.mkdir(parents=True, exist_ok=True)
        # create output path .md in the output directory based on input file name + "_transcribed"
        output_md_path = out_dir / (pathlib.Path(file_path).stem + "_transcribed.md")

        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(response.text + f"\n\nOCR and transcription by {model}")  # type: ignore
            print(f"PDF transcribed to markdown and saved to {output_md_path}")
        return output_md_path

    @staticmethod
    def md_to_TTS(
        file_path,
        prompt_file="./prompts/prepare_TTS.md",
        model="gemini-3-flash-preview",
        output_dir="./out/",
    ):
        """
        Prepare markdown text for TTS using Gemini.
        """

        with open(prompt_file, "r", encoding="utf-8") as p:
            prompt = p.read()
        print("Preparing text for TTS...")

        with open(file_path, "r", encoding="utf-8") as input_md_file:
            input_md_content = input_md_file.read()

        response = Readr.client.models.generate_content(
            model=model,
            contents=[
                input_md_content,
                prompt,
            ],
        )

        if response.text is None:
            print("Error: Response text is None.")
            print("Full response:", response)
            return

        # create a subfolder for output based on input file name
        out_dir = pathlib.Path(output_dir) / pathlib.Path(file_path).stem
        out_dir.mkdir(parents=True, exist_ok=True)
        # create output path .md in the output directory based on input file name + "_TTS"
        output_md_path = out_dir / (pathlib.Path(file_path).stem + "_TTS.md")

        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(response.text + f"\n\nTTS text prepared by {model}")  # type: ignore
            print(f"Text prepared and saved to {output_md_path}")
        return output_md_path

    @staticmethod
    def translate_to_md(
        file_path,
        prompt_file="./prompts/translate.md",
        model="gemini-3-flash-preview",
        output_dir="./out/",
    ):
        """
        Translate PDF to markdown using gemini-3-flash-preview.
        Write result to a markdown file.
        """
        prompt = ""

        with open(prompt_file, "r", encoding="utf-8") as pf:
            prompt = pf.read()

        print("Uploading PDF to Gemini...")
        # Upload the file using the File API
        file_upload = Readr.client.files.upload(file=pathlib.Path(file_path))
        print(f"File uploaded: {file_upload.name}")

        print("Processing PDF to markdown using gemini-3-flash-preview...")
        response = Readr.client.models.generate_content(
            model=os.getenv("MODEL"),
            contents=[
                file_upload,
                prompt,
            ],
        )

        if response.text is None:
            print("Error: Response text is None.")
            print("Full response:", response)
            return

        # create a subfolder for output based on input file name
        out_dir = pathlib.Path(output_dir) / pathlib.Path(file_path).stem
        out_dir.mkdir(parents=True, exist_ok=True)
        # create output path .md in the output directory based on input file name + "_translated"
        output_md_path = out_dir / (pathlib.Path(file_path).stem + "_translated.md")

        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(response.text + f"\n\nOCR by {model}")  # type: ignore
            print(
                f"PDF converted to markdown using Gemini 3 and saved to {output_md_path}"
            )
        return output_md_path

    @staticmethod
    def tldr(
        file_path,
        prompt_file="./prompts/tldr.md",
        model="gemini-3-flash-preview",
        output_dir="./out/",
    ):
        """
        Read and return text content from the PDF file.
        """
        with open(prompt_file, "r", encoding="utf-8") as pf:
            prompt = pf.read()

        response = Readr.client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(
                    data=pathlib.Path(file_path).read_bytes(),
                    mime_type="application/pdf",
                ),
                prompt,
            ],
        )

        if response.text is None:
            print("Error: Response text is None.")
            print("Full response:", response)
            return

        # create a subfolder for output based on input file name
        out_dir = pathlib.Path(output_dir) / pathlib.Path(file_path).stem
        out_dir.mkdir(parents=True, exist_ok=True)
        # create output path .md in the output directory based on input file name + "_translated"
        output_md_path = out_dir / (pathlib.Path(file_path).stem + "_tldr.md")

        # Save the summary to file
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(response.text + f"\n\nTLDR by {model}")  # type: ignore
            print(f"TLDR saved to {output_md_path}")
        return output_md_path


# TODO: rework with new functions
# def process_pdf(file_path, prompt_file):


# TODO: rework with new functions
# def translate_pdf(file_path):


# --- Directory processing ---

# TODO: REWORK WITH NEW FUNCTIONS
# def process_pdfs_in_directory(directory_path, prompt_file):
# def translate_pdfs_in_directory(directory_path):


def main():
    pass


if __name__ == "__main__":
    main()
