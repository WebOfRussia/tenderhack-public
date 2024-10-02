import os

from contract.file.FileStorage import FileStorage
from contract.file.converter.DocToDocxConverter import DocToDocxConverter
from contract.file.converter.PdfToDocxConverter import PdfToDocxConverter
from contract.file.domain.FileMetadata import FileMetadata
from contract.file.domain.TemporaryFileMetadata import TemporaryFileMetadata
from contract.file.exception.ContractFileNotFoundException import ContractFileNotFoundException
from contract.file.exception.MultipleContractFilesFoundException import MultipleContractFilesFoundException
from contract.file.exception.UnsupportedFileExtensionException import UnsupportedFileExtensionException
from contract.file.reader.DocxReader import DocxReader


def extract_plain_text(contract_id: int) -> str:
    file_metadata = convert_to_docx_if_necessary(get_file_metadata_by_contract_id(contract_id))

    plain_contract_text = DocxReader.read(file_metadata)

    if isinstance(file_metadata, TemporaryFileMetadata):
        os.remove(file_metadata.absolute_path)

    return plain_contract_text


def get_file_metadata_by_contract_id(contract_id: int) -> FileMetadata:
    file_storage = FileStorage()

    filtered = [file_metadata for file_metadata in file_storage.get_files() if file_metadata.name == str(contract_id)]

    if len(filtered) == 0:
        raise ContractFileNotFoundException(contract_id)

    if len(filtered) > 1:
        raise MultipleContractFilesFoundException(contract_id)

    file_metadata = filtered[0]

    validate_file_throwing(file_metadata)

    return file_metadata


def validate_file_throwing(file_metadata: FileMetadata):
    if file_metadata.ext not in ["doc", "docx", "pdf"]:
        raise UnsupportedFileExtensionException(file_metadata.ext)


def convert_to_docx_if_necessary(file_metadata) -> FileMetadata:
    if file_metadata.ext == "docx":
        return file_metadata

    if file_metadata.ext == "doc":
        return DocToDocxConverter.convert(file_metadata)

    if file_metadata.ext == "pdf":
        return PdfToDocxConverter.convert(file_metadata)

    raise UnsupportedFileExtensionException(file_metadata.ext)
