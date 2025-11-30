import os
from config import Config
from enigma.clients.gemini import GeminiClient
from enigma.paths import Paths
from enigma.models import ResearcherResponse, ResearcherRequirement, Task
from enigma.prompts.researcher import RESEARCHER_PROMPT


class Researcher:
    def __init__(self):
        self.gemini_client = GeminiClient(model_name=Config().RESEARCHER_MODEL)

    def run(self, requirements: ResearcherRequirement) -> ResearcherResponse:
        task = Task(
            description=self._build_task(requirements),
            instructions=RESEARCHER_PROMPT,
            assignee="researcher",
            use_code=requirements.use_code,
            use_search=requirements.use_search
        )
        result = self.gemini_client.generate_object(task, ResearcherResponse)
        return result

    def _build_task(self, requirements: ResearcherRequirement):
        prompt = f"""
You are performing a subtask of step {requirements.step_number}.
The task: {requirements.description}
The files you expect to create: {requirements.expected_files}
"""
        if requirements.use_code:
            prompt += "You must use code."
        if requirements.use_search:
            prompt += "You must use web search."
        return prompt
