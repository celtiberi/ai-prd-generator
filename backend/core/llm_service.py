from typing import Dict, Any, Optional, List, AsyncGenerator, Union
import openai
from openai import OpenAIError, APIError, RateLimitError  # Import specific error types
import logging
import time
from functools import wraps
import os
from dataclasses import dataclass
from datetime import datetime
import backoff
from .event_system import EventSystem
import uuid
import json

@dataclass
class LLMResponse:
    """Response structure for LLM interactions"""
    content: str
    model: str
    usage: Dict[str, int]
    timestamp: datetime
    request_id: str
    function_call: Optional[Dict[str, Any]] = None

class LLMService:
    """OpenAI LLM integration service with rate limiting and error handling"""
    
    def __init__(self, event_system: EventSystem, environment: str = "development"):
        self.logger = logging.getLogger(__name__)
        self.event_system = event_system
        
        # Validate environment
        valid_environments = ["development", "production"]
        if environment not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Model configuration based on environment
        self.models = {
            "development": "gpt-3.5-turbo",
            "production": "gpt-4-turbo-preview"
        }
        self.default_model = self.models[environment]
        
        # Rate limiting setup
        self.max_tokens_per_minute = 90000
        self.token_bucket = self.max_tokens_per_minute
        self.last_refill = time.time()
        
        # Model specific limits
        self.model_token_limits = {
            "gpt-3.5-turbo": 4096,
            "gpt-4-turbo-preview": 128000
        }
    
    def _refill_token_bucket(self):
        """Refill token bucket based on time elapsed"""
        now = time.time()
        time_passed = now - self.last_refill
        self.token_bucket = min(
            self.max_tokens_per_minute,
            self.token_bucket + (self.max_tokens_per_minute * time_passed / 60)
        )
        self.last_refill = now

    def _check_rate_limit(self, tokens: int) -> bool:
        """Check if we have enough tokens"""
        self._refill_token_bucket()
        if self.token_bucket >= tokens:
            self.token_bucket -= tokens
            return True
        return False
    
    def _validate_max_tokens(self, model: str, max_tokens: Optional[int]) -> None:
        """Validate max_tokens against model limits"""
        if max_tokens is not None:
            model_limit = self.model_token_limits.get(model)
            if model_limit and max_tokens > model_limit:
                raise ValueError(f"max_tokens exceeds model limit of {model_limit}")
    
    @backoff.on_exception(
        backoff.expo,
        (RateLimitError, APIError, OpenAIError),  # Use correct error types
        max_tries=3
    )
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        functions: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False
    ) -> Union[LLMResponse, AsyncGenerator[str, None]]:
        """Generate chat completion with rate limiting and error handling"""
        try:
            used_model = model or self.default_model
            self._validate_max_tokens(used_model, max_tokens)
            
            # Estimate tokens (simple estimation)
            estimated_tokens = sum(len(m["content"]) // 4 for m in messages)
            if not self._check_rate_limit(estimated_tokens):
                self.event_system.publish(
                    event_type="system.error",
                    source_agent="llm_service",
                    target_agent="system",
                    payload={
                        "error": "rate_limit_exceeded",
                        "message": "Token bucket depleted"
                    },
                    correlation_id=str(uuid.uuid4())
                )
                raise Exception("Rate limit exceeded")

            kwargs = {
                "model": used_model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream
            }
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens
            if functions is not None:
                kwargs["functions"] = functions

            if stream:
                return self._stream_response(kwargs)
            
            response = await self.client.chat.completions.create(**kwargs)
            
            # Fix function call handling
            function_call = None
            message = response.choices[0].message
            if hasattr(message, 'function_call') and message.function_call is not None:
                function_call = {
                    "name": message.function_call.name,
                    "arguments": json.loads(message.function_call.arguments)
                }
            
            llm_response = LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage={"total_tokens": response.usage.total_tokens},
                timestamp=datetime.now(),
                request_id=response.id,
                function_call=function_call
            )
            
            # Update token bucket with actual usage
            self.token_bucket -= response.usage.total_tokens
            
            return llm_response
            
        except Exception as e:
            self.logger.error(f"Error in LLM request: {str(e)}")
            self.event_system.publish(
                event_type="system.error",
                source_agent="llm_service",
                target_agent="system",
                payload={
                    "error": "llm_error",
                    "message": str(e)
                },
                correlation_id=str(uuid.uuid4())
            )
            raise 

    async def _stream_response(self, kwargs: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Handle streaming responses"""
        try:
            async for chunk in await self.client.chat.completions.create(**kwargs):
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            self.logger.error(f"Error in stream: {str(e)}")
            self.event_system.publish(
                event_type="system.error",
                source_agent="llm_service",
                target_agent="system",
                payload={
                    "error": "stream_error",
                    "message": str(e)
                },
                correlation_id=str(uuid.uuid4())
            )
            raise

    @backoff.on_exception(
        backoff.expo,
        (RateLimitError, APIError, OpenAIError),  # Use correct error types
        max_tries=3
    )
    async def generate_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-ada-002"
    ) -> List[List[float]]:
        """Generate embeddings for given texts"""
        # Validate model
        valid_embedding_models = ["text-embedding-ada-002"]
        if model not in valid_embedding_models:
            raise ValueError(f"Model must be one of: {valid_embedding_models}")
            
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
            
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
            self.event_system.publish(
                event_type="system.error",
                source_agent="llm_service",
                target_agent="system",
                payload={
                    "error": "embedding_error",
                    "message": str(e)
                },
                correlation_id=str(uuid.uuid4())
            )
            raise 

    def get_token_usage(self) -> Dict[str, int]:
        """Get current token usage statistics"""
        return {
            "remaining_tokens": self.token_bucket,
            "max_tokens_per_minute": self.max_tokens_per_minute
        }
    
    def reset_rate_limit(self):
        """Reset rate limiting counters"""
        self.token_bucket = self.max_tokens_per_minute
        self.last_refill = time.time()