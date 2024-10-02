import os
import pathlib
import subprocess

from contract.file.FileStorage import FILE_STORAGE_PATH
from contract.file.domain.FileMetadata import FileMetadata
from contract.file.domain.TemporaryFileMetadata import TemporaryFileMetadata

TEMP_FILE_STORAGE_PATH = os.path.join(FILE_STORAGE_PATH, "tmp")


class DocToDocxConverter:

    @staticmethod
    def convert(file_metadata: FileMetadata) -> TemporaryFileMetadata:
        subprocess.run([
            "soffice",
            "--headless",
            "--convert-to",
            "docx",
            "--outdir",
            TEMP_FILE_STORAGE_PATH,
            file_metadata.absolute_path
        ])

        return TemporaryFileMetadata(pathlib.Path(os.path.join(TEMP_FILE_STORAGE_PATH, f"{file_metadata.name}.docx")))
