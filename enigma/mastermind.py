from pydantic import BaseModel, PrivateAttr

from config import Config
from enigma.clients.gemini import GeminiClient
from enigma.models import MastermindStrategy, Task
from enigma.prompts.mastermind import MASTERMIND_PROMPT
from enigma.library import Library


class Mastermind(BaseModel):
    _gemini_client: GeminiClient = PrivateAttr()
    _library: Library = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._gemini_client = GeminiClient(model_name=Config().ORCHESTRATOR_MODEL)
        self._library = Library()

    def run(self, task: str) -> MastermindStrategy:
        print(f"Running mastermind: {task}")
        prompt = f"""
        Your task: {task}.
        You previous reports: {self.get_context()}
        """
        requirements = Task(
            description=prompt,
            instructions=MASTERMIND_PROMPT,
            assignee="mastermind",
            use_code=False,
            use_search=True
        )
        strategy = self._gemini_client.generate_object(requirements, MastermindStrategy)
        return strategy
    
    def get_context(self) -> str:
        context = self._library.get_all_manager_reports()
        if not context:
            return "There is no context yet. This is the start of the project."
        return context


if __name__ == "__main__":
    mastermind = Mastermind()
    response = mastermind.run(
        task="Translate the Voinych Manuscript to English."
    )
    print(response)
