from pydantic import BaseModel, model_validator
from typing import Literal

Assignee = Literal["mastermind", "manager", "researcher"]

class Task(BaseModel):
    description: str
    instructions: str
    assignee: Assignee
    use_code: bool
    use_search: bool


class ManagerRequirement(BaseModel):
    step_number: int
    title: str
    description: str


class ResearcherRequirement(BaseModel):
    step_number: int
    title: str
    description: str
    expected_files: list[str]
    use_code: bool = False
    use_search: bool = False

    @model_validator(mode='after')
    def validate_tools(self):
        if self.use_code and self.use_search:
            raise ValueError("Subtask cannot use both code and search")
        return self
    

class ManagerResponse(BaseModel):
    title: str
    prev_step_report: str
    is_human_intervention_required: bool
    is_goal_reached: bool
    researhers_requirements: list[ResearcherRequirement]
    git_commit_message: str


class ResearcherResponse(BaseModel):
    title: str
    report: str


class Sprint(BaseModel):
    goal: str
    title: str = "Untitled Sprint"
    managers_requirements: list[ManagerRequirement]


class MastermindStrategy(BaseModel):
    sprints: list[Sprint]
    report: str
