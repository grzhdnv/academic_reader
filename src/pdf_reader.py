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

    # def test3(self):
    #     """
    #     Test gemini-3-flash-preview call without pdf processing.
    #     """
    #     response = self.client.models.generate_content(
    #         model="gemini-3-flash-preview",
    #         contents="Write a short poem about the sea in the style of Shakespeare.",
    #     )

    #     print("Response:")
    #     print(response.text)

    def pdf_to_md(self):
        """
        Convert PDF to markdown using GenAI.
        Write result to a markdown file.
        """
        prompt = ""

        with open("pdf_to_md.md", "r", encoding="utf-8") as prompt_file:
            prompt = prompt_file.read()

        print("Processing PDF to markdown...")
        print(os.getenv("MODEL"))
        response = self.client.models.generate_content(
            model=os.getenv("MODEL"),
            contents=[
                types.Part.from_bytes(
                    data=self.file_path.read_bytes(),
                    mime_type="application/pdf",
                ),
                prompt,
            ],
        )

        # TODO: gemini-3-flash-preview currently fails.
        # file_upload = self.client.files.upload(file=self.file_path)

        # print("File uploaded. Generating content...")

        # response = self.client.models.generate_content(
        #     model="gemini-3-flash-preview",  # Ensure the string is correct
        #     contents=[
        #         file_upload,
        #         prompt,
        #     ],
        # )

        # print("Done. Writing to file...")
        # print(response.candidates[0].content)  # type: ignore
        # print("\n" + response.text)

        with open("test1.md", "w", encoding="utf-8") as f:
            f.write(response.candidates[0].content)  # type: ignore
            print("PDF converted to markdown and saved to test.md")

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


def process_pdf(file_path):
    pdf_reader = PDFReader(file_path)
    pdf_reader.pdf_to_md()


process_pdf("./bio/Dorival_2006/02_Ch01.pdf")

# pdf_reader = PDFReader("./bio/Dorival_2006/02_Ch01.pdf")
# pdf_reader.test3()
