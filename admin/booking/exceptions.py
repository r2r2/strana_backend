class InvalidURLException(Exception):
    def __init__(self, message: str = "Invalid URL") -> None:
        self.message = message
        super().__init__(self.message)


class ConnectCabinetError(Exception):
    def __init__(self, message: str = "Connect cabinet error") -> None:
        self.message = message
        super().__init__(self.message)
