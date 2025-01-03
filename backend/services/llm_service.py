from typing import List, Dict, Any
from openai import AsyncOpenAI
import json
import asyncio

class LLMService:
    def __init__(self, api_key=None):
        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = "gpt-4-turbo-preview"
        self.default_timeout = 60  # Increase timeout to 60 seconds

    async def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        """Get a chat completion from the LLM"""
        try:
            async with asyncio.timeout(self.default_timeout):
                response = await self.client.chat.completions.create(
                    model=self.default_model,
                    messages=messages,
                    temperature=temperature
                )
                return {
                    "status": "success",
                    "content": response.choices[0].message.content
                }
        except asyncio.TimeoutError:
            print(f"LLM request timed out after {self.default_timeout} seconds")
            return {
                "status": "error",
                "error": f"Request timed out after {self.default_timeout} seconds"
            }
        except Exception as e:
            print(f"Chat completion error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def structured_output(self, messages: List[Dict[str, str]], output_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Get structured output from LLM following a schema"""
        try:
            # Add schema to system message
            schema_message = {
                "role": "system",
                "content": f"""You are a structured data generator.
                Output must be valid JSON matching this schema:
                {json.dumps(output_schema, indent=2)}
                
                Only respond with the JSON, no other text."""
            }
            
            all_messages = [schema_message] + messages
            
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=all_messages,
                temperature=0.7,
                response_format={"type": "json_object"}  # Force JSON response
            )

            # Parse response
            try:
                content = response.choices[0].message.content
                parsed_data = json.loads(content)
                return {
                    "status": "success",
                    "data": parsed_data
                }
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {str(e)}\nContent: {content}")
                return {
                    "status": "error",
                    "error": f"Failed to parse JSON: {str(e)}"
                }

        except Exception as e:
            print(f"LLM Service Error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 