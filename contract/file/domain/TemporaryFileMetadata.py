from pathlib import Path

from contract.file.domain.FileMetadata import FileMetadata


class TemporaryFileMetadata(FileMetadata):
    def __init__(self, path: Path):
        super().__init__(path)
