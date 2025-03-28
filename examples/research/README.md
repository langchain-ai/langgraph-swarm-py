# Swarm Researcher Example

A two-phase multi-agent system that demonstrates an effective collaborative approach to planning and research tasks. This example showcases a pattern used in many deep research systems:

1. **Planning Phase**: A dedicated planner agent clarifies requirements, reads documentation, and develops a structured approach
2. **Research Phase**: A researcher agent implements the solution based on the planner's guidance

## Quickstart

```bash
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev
```

## How It Works

- The system starts with the **planner agent** that:
  - Analyzes the user's request
  - Reads relevant documentation
  - Asks clarifying questions to refine scope
  - Creates a structured plan with clear objectives
  - Identifies the most relevant resources for implementation
  - Hands off to the researcher agent

- The **researcher agent** then:
  - Follows the structured plan from the planner
  - Reads the recommended documentation sources
  - Implements the solution to satisfy all requirements
  - Can request additional planning if needed

This pattern demonstrates how breaking complex tasks into planning and execution phases can lead to more thorough, well-researched outcomes.

