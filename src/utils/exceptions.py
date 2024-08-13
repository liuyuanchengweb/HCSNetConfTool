class CreateDCSWConfigBaseException(Exception):
    pass


class SheetDeletion(CreateDCSWConfigBaseException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f'unknown sheet {self.value}'


class DevConfLoadDataError(CreateDCSWConfigBaseException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f'unknown dev config file name {self.value}'
