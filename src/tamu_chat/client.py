"""Main client class for TAMU Chat API."""
import json
import requests
from typing import Union, List, Dict, Any, Optional, Iterator
from requests.exceptions import RequestException, ConnectionError, Timeout

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


class TAMUChatClient:
    """
    Client for interacting with TAMU Chat API.
    
    Example:
        >>> client = TAMUChatClient(api_key="sk-...")
        >>> result = client.chat_completion("What is Python?")
        >>> print(result.text)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize TAMU Chat client.
        
        Args:
            api_key: API key for authentication. If not provided, will try to get
                    from TAMU_CHAT_API_KEY environment variable.
            base_url: Base URL for the API. If not provided, will use default or
                     TAMU_CHAT_BASE_URL environment variable.
        
        Raises:
            AuthenticationError: If API key is not provided and not found in environment.
        """
        self.api_key = api_key or get_api_key()
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Provide it as argument or set TAMU_CHAT_API_KEY environment variable."
            )
        
        self.base_url = (base_url or get_base_url()).rstrip('/')
        
        # Create session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def chat_completion(
        self,
        messages: Union[str, List[Dict[str, str]]],
        model: str = "protected.o3",
        bypass_filter: bool = False,
        stream: bool = False
    ) -> Union[ChatCompletionResponse, Iterator[Dict[str, Any]]]:
        """
        Generate chat completion.
        
        Args:
            messages: String or list of message dictionaries with 'role' and 'content' keys.
                     Example: [{"role": "user", "content": "Hello!"}]
            model: Model ID to use (default: "protected.o3")
            bypass_filter: Whether to bypass content filtering (default: False)
            stream: Whether to stream response. If True, returns an iterator of chunks.
                   If False, returns a ChatCompletionResponse object.
        
        Returns:
            If stream=False: ChatCompletionResponse object with text, full_response, model, id
            If stream=True: Iterator of chunk dictionaries
        
        Raises:
            APIError: If API returns an error
            AuthenticationError: If authentication fails
            InvalidModelError: If model is invalid
            NoResponseError: If no valid response received
            NetworkError: If network error occurs
            JSONDecodeError: If response cannot be decoded
        
        Example:
            >>> # Simple string input
            >>> result = client.chat_completion("What is Python?")
            >>> print(result.text)
            
            >>> # Message list input
            >>> messages = [{"role": "user", "content": "Hello!"}]
            >>> result = client.chat_completion(messages)
            
            >>> # Different model
            >>> result = client.chat_completion("Hello", model="protected.gpt-4o")
            
            >>> # With bypass filter
            >>> result = client.chat_completion("Hello", bypass_filter=True)
        """
        # Convert string to message format if needed
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        # Validate messages format
        if not isinstance(messages, list) or not messages:
            raise ValueError("messages must be a non-empty list of message dictionaries or a string")
        
        # Prepare request
        url = f"{self.base_url}/chat/completions"
        params = {"bypass_filter": str(bypass_filter).lower()}
        data = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        
        try:
            # Make request
            response = self.session.post(
                url,
                json=data,
                params=params,
                stream=True  # Always stream to handle both formats
            )
            
            # Handle HTTP errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            elif response.status_code == 404:
                raise InvalidModelError(f"Model '{model}' not found")
            elif not response.ok:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', {}).get('message', response.text)
                except:
                    error_message = f"API error: {response.status_code} - {response.text}"
                raise APIError(error_message, status_code=response.status_code)
            
            # Handle streaming response
            if stream:
                return self._handle_streaming_response(response)
            else:
                return self._handle_non_streaming_response(response, model)
        
        except (ConnectionError, Timeout) as e:
            raise NetworkError(f"Network error: {str(e)}")
        except RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise JSONDecodeError(f"Failed to decode JSON response: {str(e)}")
        except (APIError, AuthenticationError, InvalidModelError, NoResponseError):
            raise
        except Exception as e:
            raise TAMUChatError(f"Unexpected error: {str(e)}")
    
    def _handle_non_streaming_response(
        self,
        response: requests.Response,
        model: str
    ) -> ChatCompletionResponse:
        """
        Handle non-streaming response (JSON or SSE format).
        
        Args:
            response: Response object
            model: Model name used in request
        
        Returns:
            ChatCompletionResponse object
        """
        content_type = response.headers.get('Content-Type', '')
        
        # Check if it's regular JSON (not SSE)
        if 'application/json' in content_type and 'text/event-stream' not in content_type:
            # Regular JSON response - single line
            content = ''
            for line in response.iter_lines():
                if line:
                    content = line.decode('utf-8')
                    break  # JSON response is a single line
            
            try:
                full_response = json.loads(content)
            except json.JSONDecodeError as e:
                raise JSONDecodeError(f"Failed to parse JSON response: {str(e)}")
            
            # Extract text from response
            if 'choices' in full_response and len(full_response['choices']) > 0:
                text = full_response['choices'][0].get('message', {}).get('content', '')
            else:
                text = ""
            
            return ChatCompletionResponse.from_api_response(full_response, model)
        
        else:
            # SSE stream format - aggregate chunks
            return self._aggregate_sse_stream(response, model)
    
    def _aggregate_sse_stream(
        self,
        response: requests.Response,
        model: str
    ) -> ChatCompletionResponse:
        """
        Aggregate SSE stream into a single response.
        
        Args:
            response: Response object
            model: Model name used in request
        
        Returns:
            ChatCompletionResponse object
        """
        full_content = ""
        first_chunk = None
        response_id = ""
        created_time = 0
        finish_reason = "stop"
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                
                # Handle SSE format: lines starting with "data: "
                if line.startswith('data: '):
                    data_str = line[6:].strip()
                    if data_str == '[DONE]':
                        break
                    if not data_str:
                        continue
                    
                    try:
                        chunk = json.loads(data_str)
                        
                        # Track first chunk for metadata
                        if first_chunk is None:
                            first_chunk = chunk
                            response_id = chunk.get('id', '')
                            created_time = chunk.get('created', 0)
                        
                        # Extract content from delta
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            choice = chunk['choices'][0]
                            delta = choice.get('delta', {})
                            
                            # Extract content from delta
                            if 'content' in delta and delta.get('content'):
                                full_content += delta['content']
                            
                            # Check for finish reason
                            if 'finish_reason' in choice and choice.get('finish_reason'):
                                finish_reason = choice['finish_reason']
                    
                    except json.JSONDecodeError:
                        continue
        
        if first_chunk is None:
            raise NoResponseError("No valid chunks received from SSE stream")
        
        # Build full response from SSE chunks
        full_response = {
            "id": response_id,
            "object": "chat.completion",
            "created": created_time,
            "model": first_chunk.get('model', model),
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": full_content
                },
                "finish_reason": finish_reason
            }]
        }
        
        return ChatCompletionResponse.from_api_response(full_response, model)
    
    def _handle_streaming_response(
        self,
        response: requests.Response
    ) -> Iterator[Dict[str, Any]]:
        """
        Handle streaming response (SSE format).
        
        Args:
            response: Response object
        
        Yields:
            Dictionary chunks from the stream
        """
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                
                if line.startswith('data: '):
                    data_str = line[6:].strip()
                    if data_str == '[DONE]':
                        break
                    if not data_str:
                        continue
                    
                    try:
                        chunk = json.loads(data_str)
                        yield chunk
                    except json.JSONDecodeError:
                        continue
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models from the API.
        
        Returns:
            List of model dictionaries. Each model dict contains 'id', 'name', and other model details.
            The models are extracted from the 'data' key in the API response.
        
        Raises:
            APIError: If API returns an error
            AuthenticationError: If authentication fails
            NetworkError: If network error occurs
        
        Example:
            >>> models = client.list_models()
            >>> for model in models:
            ...     print(f"{model['id']} - {model['name']}")
        """
        url = f"{self.base_url}/models"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            elif not response.ok:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', {}).get('message', response.text)
                except:
                    error_message = f"API error: {response.status_code} - {response.text}"
                raise APIError(error_message, status_code=response.status_code)
            
            # Parse response JSON
            response_data = response.json()
            
            # Extract models from 'data' key
            if isinstance(response_data, dict) and 'data' in response_data:
                models = response_data['data']
                if isinstance(models, list):
                    return models
                else:
                    # If data is not a list, wrap it
                    return [models] if models else []
            elif isinstance(response_data, list):
                # If response is already a list, return it directly
                return response_data
            else:
                # Unexpected format, return empty list
                return []
        
        except (ConnectionError, Timeout) as e:
            raise NetworkError(f"Network error: {str(e)}")
        except RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise JSONDecodeError(f"Failed to decode JSON response: {str(e)}")
        except (APIError, AuthenticationError):
            raise
        except Exception as e:
            raise TAMUChatError(f"Unexpected error: {str(e)}")

