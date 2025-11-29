import os
from typing import Type, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text

    def generate_object(self, prompt: str, schema: Type[T]) -> T:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )
        # The new SDK usually populates response.parsed with the pydantic object
        # if response_schema is passed as a Pydantic model.
        # However, to be safe and consistent, we can also validate the JSON.
        # Let's try to return parsed if available, else validate text.
        
        if hasattr(response, "parsed") and response.parsed is not None:
             # If the SDK returns a Pydantic instance directly (some versions do)
             if isinstance(response.parsed, schema):
                 return response.parsed
             # If it returns a dict or something else, we might need to validate.
             # But let's stick to the safe 'validate_json' on text for now 
             # unless we know the specific behavior of this version.
             pass
             
        return schema.model_validate_json(response.text)
