class MultipleContractFilesFoundException(Exception):
    def __init__(self, contract_id: int):
        super().__init__(f"Для контракта с ID = {contract_id} было найдено несколько файлов")
