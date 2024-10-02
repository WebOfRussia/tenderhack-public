from pathlib import Path


class FileMetadata:
    def __init__(self, path: Path):
        self.name = path.stem
        self.ext = path.suffix[1:]
        self.full_name = path.name
        self.absolute_path = path.absolute()
