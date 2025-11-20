"""Configuration management for TAMU Chat API."""
import os
from typing import Optional

# Try to load from .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass


def get_api_key() -> Optional[str]:
    """
    Get API key from environment variable or .env file.
    
    Checks in order:
    1. TAMU_CHAT_API_KEY environment variable
    2. .env file (if python-dotenv is installed)
    
    Returns:
        API key string or None if not found
    """
    return os.getenv('TAMU_CHAT_API_KEY')


def get_base_url() -> str:
    """
    Get base URL from environment variable or return default.
    
    Checks in order:
    1. TAMU_CHAT_BASE_URL environment variable
    2. .env file (if python-dotenv is installed)
    3. Default URL
    
    Returns:
        Base URL string
    """
    return os.getenv('TAMU_CHAT_BASE_URL', 'https://chat-api.tamu.ai/openai')

