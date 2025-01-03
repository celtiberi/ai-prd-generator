import pytest
from unittest.mock import Mock, patch, AsyncMock
import openai
from datetime import datetime
from backend.core.llm_service import LLMService, LLMResponse
from backend.core.event_system import EventSystem

@pytest.fixture
def event_system():
    return EventSystem()

@pytest.fixture
def llm_service(event_system):
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        return LLMService(event_system)

@pytest.fixture(autouse=True)
def reset_llm_service(llm_service):
    """Reset LLM service state between tests"""
    yield
    llm_service.reset_rate_limit()

@pytest.mark.asyncio
async def test_chat_completion_success(llm_service):
    """Test successful chat completion"""
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(
        content="Test response",
        function_call=None  # Add this to avoid JSON serialization error
    ))]
    mock_response.model = "gpt-3.5-turbo"
    mock_response.usage = Mock(total_tokens=10)
    mock_response.id = "test_id"
    
    mock_client = Mock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    llm_service.client = mock_client
    
    response = await llm_service.generate_chat_completion([
        {"role": "user", "content": "Hello"}
    ])
    
    assert isinstance(response, LLMResponse)
    assert response.content == "Test response"
    assert response.model == "gpt-3.5-turbo"
    assert response.usage == {"total_tokens": 10}
    assert isinstance(response.timestamp, datetime)
    assert response.request_id == "test_id"

@pytest.mark.asyncio
async def test_rate_limiting(llm_service):
    """Test rate limiting functionality"""
    llm_service.token_bucket = 0  # Deplete token bucket
    
    with pytest.raises(Exception) as exc_info:
        await llm_service.generate_chat_completion([
            {"role": "user", "content": "Hello" * 1000}  # Large message
        ])
    
    assert "Rate limit exceeded" in str(exc_info.value)

@pytest.mark.asyncio
async def test_api_error_handling(llm_service):
    """Test API error handling"""
    # Create mock request for APIError
    mock_request = Mock()
    mock_request.method = "POST"
    mock_request.url = "https://api.openai.com/v1/chat/completions"
    
    # Create mock client that raises proper APIError
    mock_client = Mock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=openai.APIError(
            message="API Error",
            request=mock_request,
            body={"error": {"message": "API Error"}}
        )
    )
    llm_service.client = mock_client
    
    with pytest.raises(openai.APIError):
        await llm_service.generate_chat_completion([
            {"role": "user", "content": "Hello"}
        ])

def test_token_bucket_refill(llm_service):
    """Test token bucket refill mechanism"""
    initial_tokens = llm_service.token_bucket
    llm_service.token_bucket = 0
    
    # Wait a bit
    import time
    time.sleep(0.1)
    
    llm_service._refill_token_bucket()
    assert llm_service.token_bucket > 0
    assert llm_service.token_bucket <= initial_tokens 

@pytest.mark.asyncio
async def test_environment_model_selection():
    """Test model selection based on environment"""
    prod_llm = LLMService(event_system, environment="production")
    dev_llm = LLMService(event_system, environment="development")
    
    assert prod_llm.default_model == "gpt-4-turbo-preview"
    assert dev_llm.default_model == "gpt-3.5-turbo"

@pytest.mark.asyncio
async def test_embeddings_generation(llm_service):
    """Test embeddings generation"""
    mock_embedding = Mock(embedding=[0.1, 0.2, 0.3])
    mock_response = Mock(data=[mock_embedding])
    
    mock_client = Mock()
    mock_client.embeddings.create = AsyncMock(return_value=mock_response)
    llm_service.client = mock_client
    
    embeddings = await llm_service.generate_embeddings(["test text"])
    
    assert len(embeddings) == 1
    assert embeddings[0] == [0.1, 0.2, 0.3] 

def test_invalid_environment(event_system):
    """Test invalid environment raises error"""
    with pytest.raises(ValueError) as exc_info:
        LLMService(event_system, environment="invalid")
    assert "Environment must be one of" in str(exc_info.value)

@pytest.mark.asyncio
async def test_invalid_embedding_model(llm_service):
    """Test invalid embedding model raises error"""
    with pytest.raises(ValueError) as exc_info:
        await llm_service.generate_embeddings(["test"], model="invalid-model")
    assert "Model must be one of" in str(exc_info.value)

def test_token_usage_stats(llm_service):
    """Test token usage statistics"""
    stats = llm_service.get_token_usage()
    assert stats["remaining_tokens"] == llm_service.max_tokens_per_minute
    assert stats["max_tokens_per_minute"] == 90000

def test_rate_limit_reset(llm_service):
    """Test rate limit reset"""
    llm_service.token_bucket = 0
    llm_service.reset_rate_limit()
    assert llm_service.token_bucket == llm_service.max_tokens_per_minute 

@pytest.mark.asyncio
async def test_max_tokens_validation(llm_service):
    """Test max_tokens validation"""
    with pytest.raises(ValueError) as exc_info:
        await llm_service.generate_chat_completion(
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5000  # Exceeds gpt-3.5-turbo limit
        )
    assert "exceeds model limit" in str(exc_info.value)

@pytest.mark.asyncio
async def test_function_calling(llm_service):
    """Test function calling support"""
    functions = [{
        "name": "get_weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            }
        }
    }]
    
    # Create a properly structured function call response
    function_call = Mock()
    function_call.name = "get_weather"  # Use attribute instead of Mock name
    function_call.arguments = '{"location": "London", "unit": "celsius"}'
    
    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(
                content="",
                function_call=function_call
            )
        )
    ]
    mock_response.model = "gpt-3.5-turbo"
    mock_response.usage = Mock(total_tokens=10)
    mock_response.id = "test_id"
    
    mock_client = Mock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    llm_service.client = mock_client
    
    response = await llm_service.generate_chat_completion(
        messages=[{"role": "user", "content": "What's the weather in London?"}],
        functions=functions
    )
    
    assert response.function_call == {
        "name": "get_weather",
        "arguments": {"location": "London", "unit": "celsius"}
    }

@pytest.mark.asyncio
async def test_streaming_response(llm_service):
    """Test streaming response"""
    # Create an async generator for streaming
    async def mock_stream():
        yield Mock(choices=[Mock(delta=Mock(content="Hello"))])
        yield Mock(choices=[Mock(delta=Mock(content=" World"))])
    
    mock_client = Mock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_stream())
    llm_service.client = mock_client
    
    collected_text = ""
    async for chunk in await llm_service.generate_chat_completion(
        messages=[{"role": "user", "content": "Say hello"}],
        stream=True
    ):
        collected_text += chunk
    
    assert collected_text == "Hello World" 