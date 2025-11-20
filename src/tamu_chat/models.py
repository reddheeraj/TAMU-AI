"""Response models for TAMU Chat API."""
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class ChatCompletionResponse:
    """Response model for chat completion."""
    text: str
    full_response: Dict[str, Any]
    model: str
    id: str
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any], model: Optional[str] = None) -> 'ChatCompletionResponse':
        """
        Create ChatCompletionResponse from API response.
        
        Args:
            response: Full API response dictionary
            model: Model name (if not in response)
        
        Returns:
            ChatCompletionResponse instance
        """
        # Extract text from response
        if 'choices' in response and len(response['choices']) > 0:
            choice = response['choices'][0]
            if 'message' in choice:
                text = choice['message'].get('content', '')
            elif 'delta' in choice:
                text = choice['delta'].get('content', '')
            else:
                text = ''
        else:
            text = ''
        
        # Extract model name
        model_name = response.get('model', model) or 'unknown'
        
        # Extract ID
        response_id = response.get('id', '')
        
        return cls(
            text=text,
            full_response=response,
            model=model_name,
            id=response_id
        )
    
    def __str__(self) -> str:
        return f"ChatCompletionResponse(model={self.model}, id={self.id[:20]}...)"

