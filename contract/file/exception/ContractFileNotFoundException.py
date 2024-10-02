class ContractFileNotFoundException(Exception):
    def __init__(self, contract_id: int):
        super().__init__(f"Тело файла для контракта с ID = {contract_id} не найден")
