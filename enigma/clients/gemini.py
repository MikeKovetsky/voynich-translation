from datetime import datetime
import json
import os
from typing import Type, TypeVar

from google import genai
from config import Config
from google.genai import types
from pydantic import BaseModel

from enigma.models import Task
from enigma.paths import Paths

T = TypeVar("T", bound=BaseModel)


search_tool = types.Tool(
    google_search=types.GoogleSearch()
)
code_tool = types.Tool(
    code_execution=types.ToolCodeExecution
)


class GeminiClient:
    def __init__(self, model_name: str):
        api_key = Config().GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_object(self, task: Task, schema: Type[T]) -> T:
        tools = []
        if task.use_search:
            tools.append(search_tool)
        if task.use_code:
            tools.append(code_tool)
        raw_response = self.client.models.generate_content(
            model=self.model_name,
            contents=task.description,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                system_instruction=task.instructions,
                tools=tools,
                # thinking_config=types.ThinkingConfig(
                #     thinking_budget=-1,
                #     thinking_level=types.ThinkingLevel.HIGH,
                # ),
            ),
        )
        
        if raw_response.usage_metadata:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            usage_dir = os.path.join(Paths.usage_metadata, task.assignee)
            os.makedirs(usage_dir, exist_ok=True)
            with open(os.path.join(usage_dir, f"{timestamp}.json"), "w") as f:
                json.dump(raw_response.usage_metadata.model_dump(), f)
                print(f"total_token_count: {raw_response.usage_metadata.total_token_count}")

        if raw_response.prompt_feedback:
            print("GEMINI GAVE PROMPT FEEDBACK:", raw_response.prompt_feedback)
             
        return raw_response.parsed
    

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text


if __name__ == "__main__":
    GEMINI_CLIENT = GeminiClient(model_name="gemini-2.0-flash-exp")
    print(GEMINI_CLIENT.generate("Hello, world!"))
