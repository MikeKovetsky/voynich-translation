import os
from pydantic import BaseModel, PrivateAttr

from config import Config
from enigma.clients.gemini import GeminiClient
from enigma.paths import Paths
from enigma.prompts.manager import MANAGER_PROMPT
from enigma.models import ManagerRequirement, ManagerResponse, Task, ResearcherRequirement, ResearcherResponse


class Manager(BaseModel):
    _gemini_client: GeminiClient = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._gemini_client = GeminiClient(model_name=Config().ORCHESTRATOR_MODEL)

    def run(self, description: str) -> ManagerResponse:
        task = Task(
            description=description,
            instructions=MANAGER_PROMPT,
            assignee="manager",
            use_code=False,
            use_search=True
        )
        response = self._gemini_client.generate_object(task, ManagerResponse)
        return response
    
    def summarize(self, task_description: str, researcher_reports: list[ResearcherResponse]) -> str:
        reports_text = "\n\n".join([f"Report from {r.title}:\n{r.report}" for r in researcher_reports])
        prompt = f"""
        You are a Manager summarizing the work of your researchers.
        Task: {task_description}
        
        Researcher Reports:
        {reports_text}
        
        Create a comprehensive summary report of the progress made, findings, and any issues.
        """
        return self._gemini_client.generate(prompt)


if __name__ == "__main__":
    orchestrator = Manager()
    response = orchestrator.run(
        description="Translate the Voinych Manuscript to English."
    )
    print(response)
