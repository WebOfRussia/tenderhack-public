class UnsupportedFileExtensionException(Exception):
    def __init__(self, extension: str):
        super().__init__(f"Файлы с расришением {extension} на данный момент не поддерживаются")
