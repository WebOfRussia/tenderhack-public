import os
import pathlib

from contract import ROOT_DIR
from contract.file.domain.FileMetadata import FileMetadata

FILE_STORAGE_PATH = os.path.join(ROOT_DIR, "file", "storage")


class FileStorage:
    def __init__(self):
        self.items = pathlib.Path(FILE_STORAGE_PATH).iterdir()

    def get_files(self) -> list[FileMetadata]:
        return [FileMetadata(item) for item in self.items if item.is_file()]
