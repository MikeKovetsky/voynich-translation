import os
from typing import Type, TypeVar

import google.generativeai as genai
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    def generate_object(self, prompt: str, schema: Type[T]) -> T:
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )
        return schema.model_validate_json(response.text)
