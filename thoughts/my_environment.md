My Research Environment

I have a strong software engineering background working full-time with frontier AI. No wonder I used cursor + python for the entire research.
I read resources like https://voynich.nu/, but mostly it was cursor + LLM who did data mining.
During the first stages of the project (steps 1-50) I was wandering around hoping the approach works right away. Around step #50 I understood that this is a serious amount or research. The context was growing fast. The agent was overloaded with it. I defined the main principles of Context Hygiene and decided to launch subagents to make it safer and quicker.

I created 2 cursor rules:
- orchestrator.
- subagent.
I set alwaysApply: false and was apllying them directly in the chat.
I had an active tab "ORC_X". "Orc" stands for "Orchestrator" (a tribute to my fantasy passion) and X stands for an integer number that marks the generation of Orchestrator.
In this ORC_X I was typing @orchestrator. It produced my the requirements for subagents (usually 3 tasks).
Then I create a new cursor Agent for every task. For example task #269. And launch them with @subagent @track269_gap_report.txt.