import json
import os
import re
from typing import Dict, Any

from enigma.paths import Paths

class Library:
    def __init__(self):
        self.progress_dir = os.path.join(Paths.library, "progress")
        self.map_path = os.path.join(Paths.library, "map.json")
        os.makedirs(self.progress_dir, exist_ok=True)
        self.index: Dict[str, Any] = self._load_map()

    def _load_map(self) -> Dict[str, Any]:
        if os.path.exists(self.map_path):
            try:
                with open(self.map_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"sprints": []}
        else:
            return {"sprints": []}

    def _save_map(self) -> None:
        with open(self.map_path, 'w') as f:
            json.dump(self.index, f, indent=2)

    def _sanitize(self, name: str) -> str:
        # Replace spaces with underscores and remove non-alphanumeric chars (except - and _)
        sanitized = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
        return sanitized[:50] # Limit length

    def create_sprint(self, sprint_number: int, title: str, requirements: str) -> str:
        dirname = f"{sprint_number}_{self._sanitize(title)}"
        path = os.path.join(self.progress_dir, dirname)
        os.makedirs(path, exist_ok=True)
        
        with open(os.path.join(path, "requirements.txt"), "w") as f:
            f.write(requirements)
            
        # Update index
        sprint_entry = {
            "number": sprint_number,
            "title": title,
            "path": os.path.relpath(path, Paths.library),
            "managers": []
        }
        
        # Check if exists and update or append
        sprints = self.index.get("sprints", [])
        existing_idx = next((i for i, s in enumerate(sprints) if s.get("number") == sprint_number), -1)
        
        if existing_idx >= 0:
            sprints[existing_idx].update(sprint_entry)
        else:
            sprints.append(sprint_entry)
        
        self.index["sprints"] = sprints
        self._save_map()
        return path

    def create_manager_task(self, sprint_number: int, task_title: str, requirements: str) -> str:
        sprints = self.index.get("sprints", [])
        sprint_entry = next((s for s in sprints if s.get("number") == sprint_number), None)
        
        if not sprint_entry:
            # Fallback if sprint wasn't explicitly created (should not happen in normal flow)
            raise ValueError(f"Sprint {sprint_number} not found in index")

        sprint_path = os.path.join(Paths.library, sprint_entry["path"])
        dirname = self._sanitize(task_title)
        path = os.path.join(sprint_path, dirname)
        os.makedirs(path, exist_ok=True)
        
        with open(os.path.join(path, "requirements.txt"), "w") as f:
            f.write(requirements)
            
        manager_entry = {
            "title": task_title,
            "path": os.path.relpath(path, Paths.library),
            "research_tasks": []
        }
        
        managers = sprint_entry.get("managers", [])
        existing_idx = next((i for i, m in enumerate(managers) if m.get("title") == task_title), -1)
        
        if existing_idx >= 0:
            managers[existing_idx].update(manager_entry)
        else:
            managers.append(manager_entry)
            
        sprint_entry["managers"] = managers
        self._save_map()
        return path

    def complete_manager_task(self, sprint_number: int, task_title: str, report: str) -> None:
        sprints = self.index.get("sprints", [])
        sprint_entry = next((s for s in sprints if s.get("number") == sprint_number), None)
        if not sprint_entry: return
        
        managers = sprint_entry.get("managers", [])
        manager_entry = next((m for m in managers if m.get("title") == task_title), None)
        if not manager_entry: return
        
        full_path = os.path.join(Paths.library, manager_entry["path"])
        with open(os.path.join(full_path, "report.txt"), "w") as f:
            f.write(report)

    def create_research_task(self, sprint_number: int, manager_task_title: str, research_title: str, requirements: str) -> str:
        sprints = self.index.get("sprints", [])
        sprint_entry = next((s for s in sprints if s.get("number") == sprint_number), None)
        if not sprint_entry: 
            raise ValueError(f"Sprint {sprint_number} not found")
            
        managers = sprint_entry.get("managers", [])
        manager_entry = next((m for m in managers if m.get("title") == manager_task_title), None)
        if not manager_entry:
             raise ValueError(f"Manager task {manager_task_title} not found in sprint {sprint_number}")

        manager_path = os.path.join(Paths.library, manager_entry["path"])
        dirname = f"research_{self._sanitize(research_title)}"
        path = os.path.join(manager_path, dirname)
        os.makedirs(path, exist_ok=True)
        
        with open(os.path.join(path, "requirements.txt"), "w") as f:
            f.write(requirements)
            
        research_entry = {
            "title": research_title,
            "path": os.path.relpath(path, Paths.library)
        }
        
        research_tasks = manager_entry.get("research_tasks", [])
        existing_idx = next((i for i, r in enumerate(research_tasks) if r.get("title") == research_title), -1)
        
        if existing_idx >= 0:
            research_tasks[existing_idx].update(research_entry)
        else:
            research_tasks.append(research_entry)
        
        manager_entry["research_tasks"] = research_tasks
        self._save_map()
        return path

    def complete_research_task(self, sprint_number: int, manager_task_title: str, research_title: str, report: str) -> None:
        sprints = self.index.get("sprints", [])
        sprint_entry = next((s for s in sprints if s.get("number") == sprint_number), None)
        if not sprint_entry: return
        
        managers = sprint_entry.get("managers", [])
        manager_entry = next((m for m in managers if m.get("title") == manager_task_title), None)
        if not manager_entry: return
        
        research_tasks = manager_entry.get("research_tasks", [])
        research_entry = next((r for r in research_tasks if r.get("title") == research_title), None)
        if not research_entry: return
        
        full_path = os.path.join(Paths.library, research_entry["path"])
        with open(os.path.join(full_path, "report.txt"), "w") as f:
            f.write(report)

    def get_next_sprint_number(self) -> int:
        # Check index
        sprints = self.index.get("sprints", [])
        max_index = max((s.get("number", 0) for s in sprints), default=0)
        
        # Check filesystem
        if os.path.exists(self.progress_dir):
            for name in os.listdir(self.progress_dir):
                match = re.match(r'^(\d+)_', name)
                if match:
                    max_index = max(max_index, int(match.group(1)))
                    
        return max_index + 1

    def get_all_manager_reports(self) -> str:
        reports = []
        for sprint in self.index.get("sprints", []):
            for manager in sprint.get("managers", []):
                path = os.path.join(Paths.library, manager["path"], "report.txt")
                if os.path.exists(path):
                    with open(path, "r") as f:
                        reports.append(f"Sprint {sprint['number']} - {manager['title']}: {f.read()}")
        return "\n\n".join(reports)
