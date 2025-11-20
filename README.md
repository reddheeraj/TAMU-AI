# TAMU Chat API Python Library

Access Texas A&M University's AI services with just 2 lines of code, and use any of the provided LLMs for free! (Exclusive for Aggies)

> This library is still in development and the API may be subject to change.
> You need to get your API key from [chat.tamu.ai](https://chat.tamu.ai)

## Features

- 🚀 Simple and intuitive usage
- 🔒 Secure API key management via environment variables
- 📦 Type hints throughout for better IDE support
- 🎯 Support for multiple models (o3, GPT-4, Claude, Gemini, etc.)
- 🔄 Handles both JSON and SSE streaming responses
- ⚡ Built-in error handling with custom exceptions
- 📝 Full response objects with easy access to text content

## Installation

```bash
pip install tamu-chat
```

Or install from source:

```bash
git clone https://github.com/yourusername/tamu-chat.git
cd tamu-chat
pip install -e .
```

## Quick Start

### Basic Usage

```python
from tamu_chat import TAMUChatClient

# Initialize client with API key (or add it to the .env file)
client = TAMUChatClient(api_key="sk-your-api-key-here")

result = client.chat_completion("What is the capital of India?")
print(result.text)
# Output: "The capital of India is New Delhi."

# Access full response
print(result.model)
print(result.id)
print(result.full_response)
```

### Using Environment Variables

You can set the API key via environment variable or `.env` file:

**Option 1: Environment Variable**
```python
import os
os.environ['TAMU_CHAT_API_KEY'] = 'sk-your-api-key-here'

from tamu_chat import TAMUChatClient

# API key will be automatically loaded from environment
client = TAMUChatClient()
```

**Option 2: .env File (Recommended)**

Create a `.env` file in your project root:
```
TAMU_CHAT_API_KEY=sk-your-api-key-here
TAMU_CHAT_BASE_URL=https://chat-api.tamu.ai/openai
```

Then use the client:
```python
from tamu_chat import TAMUChatClient

# API key will be automatically loaded from .env file
client = TAMUChatClient()
```

**Note:** The library uses `python-dotenv` to automatically load `.env` files. Make sure to add `.env` to your `.gitignore` to keep your API key secure!

### Advanced Usage

```python
# Get a list of available models
models = client.list_models()
for model in models:
    print(model['id'])

# Make sure to use this model id in 'model' parameter of chat_completion()
# Different model
result = client.chat_completion(
    "Explain quantum computing",
    model="protected.gpt-4o"
)

# With bypass filter
result = client.chat_completion(
    "What is Python?",
    bypass_filter=True
)

# Multi-turn conversation
messages = [
    {"role": "user", "content": "My name is Alice."},
    {"role": "assistant", "content": "Hello Alice! How can I help you?"},
    {"role": "user", "content": "What's my name?"}
]
result = client.chat_completion(messages)
print(result.text)  # "Your name is Alice."
```

## API Reference

### TAMUChatClient

Main client class for interacting with the TAMU Chat API.

#### `__init__(api_key=None, base_url=None)`

Initialize the client.

**Parameters:**
- `api_key` (str, optional): API key for authentication. If not provided, will try to get from `TAMU_CHAT_API_KEY` environment variable.
- `base_url` (str, optional): Base URL for the API. Defaults to `https://chat-api.tamu.ai/openai`.

**Raises:**
- `AuthenticationError`: If API key is not provided and not found in environment.

#### `chat_completion(messages, model="protected.o3", bypass_filter=False, stream=False)`

Generate chat completion.

**Parameters:**
- `messages` (str | List[Dict[str, str]]): String or list of message dictionaries with 'role' and 'content' keys.
- `model` (str): Model ID to use. Default: `"protected.o3"`.
- `bypass_filter` (bool): Whether to bypass content filtering. Default: `False`.
- `stream` (bool): Whether to stream response. Default: `False`.

**Returns:**
- If `stream=False`: `ChatCompletionResponse` object
- If `stream=True`: Iterator of chunk dictionaries

**Raises:**
- `APIError`: If API returns an error
- `AuthenticationError`: If authentication fails
- `InvalidModelError`: If model is invalid
- `NoResponseError`: If no valid response received
- `NetworkError`: If network error occurs

#### `list_models()`

List available models from the API.

**Returns:**
- List of model dictionaries

**Raises:**
- `APIError`: If API returns an error
- `AuthenticationError`: If authentication fails

### ChatCompletionResponse

Response object returned by `chat_completion()`.

**Attributes:**
- `text` (str): The actual response text content
- `full_response` (dict): Complete API response object
- `model` (str): Model name used
- `id` (str): Response ID

## Error Handling

The library provides custom exceptions for better error handling:

```python
from tamu_chat import (
    TAMUChatClient,
    APIError,
    AuthenticationError,
    InvalidModelError,
    NetworkError
)

client = TAMUChatClient(api_key="sk-...")

try:
    result = client.chat_completion("Hello")
except AuthenticationError:
    print("Invalid API key")
except InvalidModelError:
    print("Model not found")
except NetworkError:
    print("Network error occurred")
except APIError as e:
    print(f"API error: {e}")
```

## Available Models

Common model IDs include:
- `protected.o3`
- `protected.gpt-4o`
- `protected.gpt-4.1`
- `protected.gpt-5`
- `protected.Claude 3.5 Sonnet`
- `protected.Claude Opus 4.1`
- `protected.gemini-2.0-flash`

To get a complete list of available models:

```python
models = client.list_models()
for model in models:
    print(model['id'])
```

## Configuration

### Environment Variables

- `TAMU_CHAT_API_KEY`: Your API key (required if not passed to constructor)
- `TAMU_CHAT_BASE_URL`: Base URL for the API (optional, defaults to `https://chat-api.tamu.ai/openai`)

## Requirements

- Python 3.11+
- requests
- python-dotenv
## Development

To contribute to this project:

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Create a new branch in your forked repository for your changes.
   ```bash
   git checkout -b <branch_name>
   ```
4. Add code to the library and test it.
   ```bash
   git add .
   git commit -m "Add <feature_name>" (Describe the changes you made)
   ```
5. Run tests:
   ```bash
   pytest tests/<test_file>.py
   ``` 
6. Test the library and raise a pull request.
   ```bash
   git push forked-repository-name <branch_name>
   ```
7. Wait for the pull request to be reviewed and merged.


## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

> If you see this error during installation via pip, please ignore or report it via issues.
```bash
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
conda-repo-cli 1.0.75 requires requests_mock, which is not installed.
anaconda-cloud-auth 0.1.4 requires pydantic<2.0, but you have pydantic 2.11.1 which is incompatible.
conda-repo-cli 1.0.75 requires clyent==1.2.1, but you have clyent 1.2.2 which is incompatible.
conda-repo-cli 1.0.75 requires requests==2.31.0, but you have requests 2.32.5 which is incompatible.
streamlit 1.30.0 requires cachetools<6,>=4.0, but you have cachetools 6.2.1 which is incompatible.
streamlit 1.30.0 requires packaging<24,>=16.8, but you have packaging 24.2 which is incompatible.
streamlit 1.30.0 requires protobuf<5,>=3.20, but you have protobuf 6.33.0 which is incompatible.
```

## Creator
- Dheeraj Mudireddy (meetdheerajreddy@gmail.com)

## Changelog

### 0.1.0 (11/20/2025)
- Initial release
- Basic chat completion support
- Model listing support
- Custom exception handling
- Environment variable configuration

