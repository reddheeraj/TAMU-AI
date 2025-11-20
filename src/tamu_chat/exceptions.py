"""Custom exceptions for TAMU Chat API."""


class TAMUChatError(Exception):
    """Base exception for TAMU Chat API errors."""
    pass


class APIError(TAMUChatError):
    """API returned an error."""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class AuthenticationError(TAMUChatError):
    """Authentication failed."""
    pass


class InvalidModelError(TAMUChatError):
    """Invalid model specified."""
    pass


class NoResponseError(TAMUChatError):
    """No valid response received from API."""
    pass


class NetworkError(TAMUChatError):
    """Network error occurred."""
    pass


class JSONDecodeError(TAMUChatError):
    """Failed to decode JSON response."""
    pass

