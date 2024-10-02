import os

from docx import Document
from docx.oxml import CT_P, CT_Tbl, CT_Row, CT_Tc
from tabulate import tabulate

from contract.file.FileStorage import FILE_STORAGE_PATH
from contract.file.domain.FileMetadata import FileMetadata

TEMP_FILE_STORAGE_PATH = os.path.join(FILE_STORAGE_PATH, "tmp")


class DocxReader:

    @staticmethod
    def read(file_metadata: FileMetadata) -> str:

        doc = Document(file_metadata.absolute_path)
        text_content = []

        for element in doc.element.body:
            if isinstance(element, CT_P):
                text_content.append(DocxReader.read_paragraph(element))
            elif isinstance(element, CT_Tbl):
                text_content.append(DocxReader.read_table(element))

        return "\n".join(text_content)

    @staticmethod
    def read_paragraph(paragraph: CT_P) -> str:
        paragraph_texts = []
        for node in paragraph.xpath('.//w:t'):
            if node.text:
                paragraph_texts.append(node.text)
        return ''.join(paragraph_texts)

    @staticmethod
    def read_table(table: CT_Tbl) -> str:
        table_data = []

        for row in table.xpath('.//w:tr'):
            table_data.append(DocxReader.read_table_row(row))

        # Convert the table to text format
        table_text = tabulate(table_data, tablefmt="grid")
        return table_text

    @staticmethod
    def read_table_row(row: CT_Row) -> list[str]:
        row_data = []
        for cell in row.xpath('.//w:tc'):
            row_data.append(DocxReader.read_table_cell(cell))
        return row_data

    @staticmethod
    def read_table_cell(cell: CT_Tc) -> str:
        cell_texts = []
        for node in cell.xpath('.//w:t'):
            if node.text:
                cell_texts.append(node.text)
        return ''.join(cell_texts)
