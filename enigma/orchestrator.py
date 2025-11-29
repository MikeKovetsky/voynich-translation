from pydantic import BaseModel, PrivateAttr

from config import Config
from enigma.clients.gemini import GeminiClient
from enigma.prompts.orchestrator import ORCHESTRATOR_PROMPT


class OrchestratorResponse(BaseModel):
    is_human_intervention_required: bool
    title: str
    tasks: list[str]


class Orchestrator(BaseModel):
    _gemini_client: GeminiClient = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._gemini_client = GeminiClient(model_name=Config().ORCHESTRATOR_MODEL)

    def run(self):
        response = self._gemini_client.generate_object(
            prompt=ORCHESTRATOR_PROMPT,
            schema=OrchestratorResponse
        )
        print(response)
        return response
    

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run()
