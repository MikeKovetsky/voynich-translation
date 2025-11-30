from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

from enigma.git import git_commit_and_push
from enigma.mastermind import Mastermind
from enigma.models import ManagerRequirement, ResearcherRequirement, Sprint, ResearcherResponse
from enigma.manager import Manager
from enigma.researcher import Researcher
from enigma.library import Library


def run_mastermind() -> None:
    library = Library()
    mastermind = Mastermind()
    genesis = "This is the GENESIS task. Define the initial stages."
    strategy = mastermind.run(task=genesis)
    sprints_queue = deque(strategy.sprints)
    
    sprint_idx = library.get_next_sprint_number()
    
    while sprints_queue:
        sprint: Sprint = sprints_queue.popleft()
        library.create_sprint(sprint_idx, sprint.title, sprint.goal)
        
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(run_manager, req, sprint_idx, library) 
                for req in sprint.managers_requirements
            ]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Manager task failed: {e}")
        
        sprint_idx += 1
        
        evaluation = "Sprints are completed. Evaluate managers' reports, adjust the strategy/sprints if necessary."
        new_strategy = mastermind.run(task=evaluation)
        if new_strategy.sprints:
            sprints_queue.extend(new_strategy.sprints)

        print(f"new_strategy: {new_strategy}")
        return


def run_manager(managers_requirements: ManagerRequirement, sprint_number: int, library: Library) -> None:
    print(f"Running manager: {managers_requirements.title}")
    manager = Manager()
    library.create_manager_task(sprint_number, managers_requirements.title, managers_requirements.description)
    manager_response = manager.run(managers_requirements.description)
    researcher_reports = []
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(run_researcher, req, sprint_number, managers_requirements.title, library) 
            for req in manager_response.researhers_requirements
        ]
        for future in as_completed(futures):
            try:
                res = future.result()
                if res:
                    researcher_reports.append(res)
            except Exception as e:
                print(f"Researcher task failed: {e}")
    
    summary = manager.summarize(managers_requirements.description, researcher_reports)
    library.complete_manager_task(sprint_number, managers_requirements.title, summary)
    
    # git_commit_and_push(f"enigma(sprint_{sprint_number}): {manager_response.git_commit_message}")


def run_researcher(researcher_requirements: ResearcherRequirement, sprint_number: int, manager_task_title: str, library: Library) -> ResearcherResponse:
    print(f"Running researcher: {researcher_requirements.title}")
    researcher = Researcher()
    
    library.create_research_task(sprint_number, manager_task_title, researcher_requirements.title, researcher_requirements.description)
    researcher_response = researcher.run(researcher_requirements)
    library.complete_research_task(sprint_number, manager_task_title, researcher_requirements.title, researcher_response.report)
    
    return researcher_response


if __name__ == "__main__":
    run_mastermind()
