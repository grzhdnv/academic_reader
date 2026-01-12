import os
import pathlib
from path_manager import PathManager

from dotenv import load_dotenv

from google import genai
from google.genai import types

load_dotenv()  # Load environment variables from .env file


# Class to handle pdf reading
class PDFReader:
    """Class to read and summarize PDF files using GenAI.

    Attributes:
        file_path (pathlib.Path): Path to the PDF file.
        client (genai.Client): GenAI client initialized with API key.
    """

    file_path: pathlib.Path  # Path to the PDF file
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))  # GenAI client

    # Initialize with file path
    def __init__(self, file_path):
        self.file_path = pathlib.Path(file_path)

    def pdf_to_md(self, prompt_file):
        """
        Convert PDF to markdown using GenAI.
        Write result to a markdown file.
        """

        with open(prompt_file, "r", encoding="utf-8") as p:
            prompt = p.read()

        print("Processing PDF to markdown...")

        response = self.client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                types.Part.from_bytes(
                    data=self.file_path.read_bytes(),
                    mime_type="application/pdf",
                ),
                prompt,
            ],
        )

        if response.text is None:
            print("Error: Response text is None.")
            print("Full response:", response)
            return

        # create a subfolder for output
        output_dir = self.file_path.parent / "tldr"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_md_path = output_dir / self.file_path.with_suffix(".md").name
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(response.text + "\n\nOCR and TLDR by Gemini 3.0 Flash")  # type: ignore
            print(f"PDF converted to markdown and saved to {output_md_path}")

    def translate_to_md_gemini3(self):
        """
        Convert PDF to markdown using gemini-3-flash-preview.
        Write result to a markdown file.
        """
        prompt = ""

        with open("translated_chapter.md", "r", encoding="utf-8") as prompt_file:
            prompt = prompt_file.read()

        print("Uploading PDF to Gemini...")
        # Upload the file using the File API
        file_upload = self.client.files.upload(file=self.file_path)
        print(f"File uploaded: {file_upload.name}")

        print("Processing PDF to markdown using gemini-3-flash-preview...")
        response = self.client.models.generate_content(
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

        new_path = self.file_path.stem + "_g3translated.md"
        output_md_path = pathlib.Path(new_path)
        print(output_md_path)
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(response.text + "\n\nOCR by Gemini 3 Flash")  # type: ignore
            print(
                f"PDF converted to markdown using Gemini 3 and saved to {output_md_path}"
            )

    def summarize(self):
        """
        Read and return text content from the PDF file.
        """
        with open("prompt.txt", "r", encoding="utf-8") as prompt_file:
            prompt = prompt_file.read()

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=self.file_path.read_bytes(),
                    mime_type="application/pdf",
                ),
                prompt,
            ],
        )
        print("Done. Writing to file...")
        return response.text

    def save_summary(self, summary_text, base_name):
        """
        Save the summary text to a markdown file in an output directory.
        """
        # Create a directory for the output if it doesn't exist
        output_dir = pathlib.Path(f"output/{base_name}")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save the summary to file
        with open(f"{output_dir}/{base_name}.md", "w", encoding="utf-8") as f:
            f.write(summary_text)
            print(f"Summary saved to {base_name}.md")

    def short_summary(self):
        """
        Generate a short summary of the previously saved summary text
        and write it to a new markdown file.
        """
        with open(
            f"{PathManager.output_dir}/{PathManager.base_name}.md",
            "r",
            encoding="utf-8",
        ) as summary_file:
            summary = summary_file.read()

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Give me a paragraph summary of the following article and bullet point main arguments made:\n\n {summary}",
        )
        print("Done. Writing to file...")
        with open(
            f"{PathManager.output_dir}/{PathManager.base_name}_short.md",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(response.text)  # type: ignore
            print(f"Summary saved to {PathManager.base_name}_short.md")


def process_pdf(file_path, prompt_file):
    pdf_reader = PDFReader(file_path)
    pdf_reader.pdf_to_md(prompt_file)


def translate_pdf(file_path):
    pdf_reader = PDFReader(file_path)
    pdf_reader.translate_to_md_gemini3()


# --- Directory processing ---


def process_pdfs_in_directory(directory_path, prompt_file):
    """Process all PDF files in a given directory and its subdirectories."""
    print(f"Searching for PDF files in {directory_path}...")
    pdf_files = list(pathlib.Path(directory_path).rglob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files.")

    for file_path in pdf_files:
        print(f"Processing {file_path}...")
        process_pdf(file_path, prompt_file)


def translate_pdfs_in_directory(directory_path):
    """Translate all PDF files in a given directory and its subdirectories."""
    print(f"Searching for PDF files in {directory_path}...")
    pdf_files = list(pathlib.Path(directory_path).rglob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files.")

    for file_path in pdf_files:
        print(f"Processing {file_path}...")
        translate_pdf(file_path)


if __name__ == "__main__":
    # --- Process a single PDF file ---
    # The original call is preserved here for single-file processing.
    process_pdf("./bio/Dorival_2006/03_Ch02.pdf", "tldr.md")

    # --- Test Gemini 3 PDF to MD ---
    # test_translate_to_md_gemini3("./bio/Dorival_2006/02_Ch01.pdf") // Currently fails because of copyright guardrails.

    # --- Process all PDFs in a directory ---
    # process_pdfs_in_directory("./bio/Dorival_2006/", "tldr.md")  # TLDR setup

    # --- Translate all PDFs in a directory ---
    # TODO: Run this
    # translate_pdfs_in_directory("./bio/Dorival_2006/missed/")

    # --- Test call without PDF processing ---
    # pdf_reader = PDFReader("./bio/Dorival_2006/02_Ch01.pdf")
    # pdf_reader.test3()
    pass
