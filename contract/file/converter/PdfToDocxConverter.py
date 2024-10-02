import os
import pathlib

from pdf2docx import Converter

from contract.file.FileStorage import FILE_STORAGE_PATH
from contract.file.domain.FileMetadata import FileMetadata
from contract.file.domain.TemporaryFileMetadata import TemporaryFileMetadata

TEMP_FILE_STORAGE_PATH = os.path.join(FILE_STORAGE_PATH, "tmp")


class PdfToDocxConverter:

    @staticmethod
    def convert(file_metadata: FileMetadata) -> TemporaryFileMetadata:
        cv = Converter(file_metadata.absolute_path)

        result_filename = os.path.join(TEMP_FILE_STORAGE_PATH, f"{file_metadata.name}.docx")

        cv.convert(result_filename, multi_processing=True)

        return TemporaryFileMetadata(pathlib.Path(result_filename))
