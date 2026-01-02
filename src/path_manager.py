import pathlib
import re


# Class for handling file paths
class PathManager:
    file_path: pathlib.Path
    file_name: str
    base_name: str
    output_dir: pathlib.Path

    # Initialize with user input
    def __init__(self, user_input):
        # Remove surrounding quotes that macOS might add
        if (user_input.startswith("'") and user_input.endswith("'")) or (
            user_input.startswith('"') and user_input.endswith('"')
        ):
            user_input = user_input[1:-1]
        self.file_path = pathlib.Path(user_input)
        self.file_name = self.file_path.stem
        self.base_name = self.get_base_name()
        self.output_dir = self.get_output_dir(self.base_name)

    def get_base_name(self):
        # Extract the author's last name and year in parentheses
        match = re.match(r"^([A-Za-z]+ ?\(\d{4}\))", self.file_name)
        if match:
            base_name = match.group(1)
        else:
            base_name = self.file_name  # fallback if pattern not found
        return base_name

    def get_output_dir(self, base_name):
        # Create a directory for the output if it doesn't exist
        output_dir = pathlib.Path(f"output/{base_name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
