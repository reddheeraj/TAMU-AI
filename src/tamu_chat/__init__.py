"""TAMU Chat API Python Library.

A simple, clean interface for interacting with the TAMU Chat API.
"""

from .client import TAMUChatClient
from .exceptions import (
    TAMUChatError,
    APIError,
    AuthenticationError,
    InvalidModelError,
    NoResponseError,
    NetworkError,
    JSONDecodeError
)
from .models import ChatCompletionResponse
from .config import get_api_key, get_base_url

__version__ = "0.1.0"

__all__ = [
    "TAMUChatClient",
    "ChatCompletionResponse",
    "TAMUChatError",
    "APIError",
    "AuthenticationError",
    "InvalidModelError",
    "NoResponseError",
    "NetworkError",
    "JSONDecodeError",
    "get_api_key",
    "get_base_url",
]

