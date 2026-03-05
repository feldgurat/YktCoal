
class OtpRateLimitError(Exception):
    pass

class SmsProviderTimeoutError(Exception):
    pass


class SmsProviderResponseError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class SmsProviderInternalError(Exception):
    pass

class TokenHasExpired(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)

class InvalidToken(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)

class InvalidTokenType(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)