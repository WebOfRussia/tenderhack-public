import uuid

from docxtpl import DocxTemplate


def render_doc(context: dict, filepath: str) -> str:
    """
    Преобразование шаблона в документ

    :param context: метаданные для формирования документа
    :param filepath: путь к шаблону файла
    :return: сгенерированный файл
    """
    random_uuid = uuid.uuid4()
    result_filename = f"{random_uuid}.docx"
    try:
        doc = DocxTemplate(filepath)
        doc.render(context)
        doc.save(f"./static/docs/{result_filename}")

        return result_filename
    except Exception:
        return filepath
