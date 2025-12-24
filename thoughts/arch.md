# Orchestrator vs Subagent Process

This document describes the research workflow between the Orchestrator (Project Lead) and Subagents (Researchers).
This approach is not new. Most coprporate/sociatal structures follow it. The main reasons are:
- Context Hygiene. Event the most modern LLMs cannot keep the context of entire project that consists of many millions of tokens.

## 1. Roles

### Orchestrator
- **Goal**: High-level strategic direction, hypothesis generation, and synthesis of results.
- **Responsibilities**:
  - Defines the research iteration.
  - Breaks down big goals into parallelizable subtasks.
  - Creates task definitions in `/tasks`.
  - Reviews and validates results produced by subagents.
  - Maintains the global project state in `progress_summary_2.md`.
  - Handles git operations (commit/push).

### Subagent
- **Goal**: Execution of specific, bounded research tasks.
- **Responsibilities**:
  - Reads specific task requirements.
  - Performs deep dives, web research, or writes Python scripts.
  - Generates raw data and analysis artifacts.
  - Summarizes findings for the Orchestrator.
  - **Constraints**: Does not modify global progress logs; operates within the scope of the assigned task.

## 2. Workflow Loop

1.  **Task Definition (Orchestrator)**
    - The Orchestrator identifies the next step in the research.
    - Creates a text file in `/tasks` (e.g., `track{ID}_{name}.txt`).
    - Specifies input requirements and expected output filenames in `/results`.

2.  **Execution (Subagent)**
    - Reads the assigned task file and `progress_summary.md` for context.
    - Writes analysis scripts in `/research`.
    - Saves intermediate and final data to `/results`.
    - **Crucial Step**: Generates a summary file `results/track-{ID}-results_summary.md` explaining findings, confidence levels, and potential issues.

3.  **Synthesis (Orchestrator)**
    - Reads the subagent's summary and inspects generated files.
    - Validates assumptions.
    - Appends a new entry to `progress_summary_2.md` (using emojis/casual style) to record the iteration.
    - Decides the next set of tasks based on these findings.

## 3. Directory Structure & Artifacts

| Directory | Role Access | Usage |
|-----------|-------------|-------|
| `/tasks` | **Orchestrator** (Write) | Contains clear, textual requirements for subagents. |
| `/research`| **Subagent** (Write) | Python scripts and analysis code. |
| `/results` | **Subagent** (Write) | Output data (JSON, MD, CSV) and the specific `*_summary.md`. |
| `progress_summary_2.md` | **Orchestrator** (Write) | Global history of the project iterations. |




