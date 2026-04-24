"""Reasoning agent - plans and thinks through complex tasks."""
import json
import logging
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class StepType(Enum):
    """Types of planning steps."""
    THINK = "think"
    ACT = "act"
    OBSERVE = "observe"
    PLAN = "plan"
    REPLAN = "replan"


@dataclass
class PlanStep:
    """A single step in a plan."""
    step_type: StepType
    description: str
    tool: Optional[str] = None
    args: dict = field(default_factory=dict)
    expected_outcome: Optional[str] = None


@dataclass
class Plan:
    """A plan containing multiple steps."""
    goal: str
    steps: list[PlanStep] = field(default_factory=list)
    current_step: int = 0
    completed: bool = False
    failed: bool = False
    error: Optional[str] = None


class ReasoningAgent:
    """Handles planning, reasoning, and task decomposition."""
    
    PLANNING_PROMPT = """You are a planning agent. Given a user task, create a step-by-step plan to accomplish it.

Available tools:
- shell: Execute shell commands
- file_read: Read files
- file_write: Write files
- app_open: Open applications
- app_close: Close applications
- search: Search for files or content

Output a JSON plan with this structure:
{
    "goal": "What we're trying to achieve",
    "steps": [
        {
            "step_type": "think|act|observe",
            "description": "What this step does",
            "tool": "tool_name",
            "args": {"key": "value"},
            "expected_outcome": "What should happen"
        }
    ]
}

Only include steps that are necessary. Be concise."""

    def __init__(self, model_manager):
        self.model_manager = model_manager
    
    async def create_plan(self, task: str) -> Optional[Plan]:
        """Create a plan for a task."""
        prompt = f"{self.PLANNING_PROMPT}\n\nTask: {task}"
        
        try:
            result = await self.model_manager.complete(prompt)
            
            # Parse JSON from response
            plan_data = self._extract_json(result)
            if not plan_data:
                logger.warning("Could not parse plan JSON")
                return None
            
            plan = Plan(
                goal=plan_data.get("goal", task),
                steps=[
                    PlanStep(
                        step_type=StepType(s.get("step_type", "act")),
                        description=s.get("description", ""),
                        tool=s.get("tool"),
                        args=s.get("args", {}),
                        expected_outcome=s.get("expected_outcome")
                    )
                    for s in plan_data.get("steps", [])
                ]
            )
            
            logger.info(f"Created plan with {len(plan.steps)} steps")
            return plan
        
        except Exception as e:
            logger.error(f"Plan creation failed: {e}")
            return None
    
    async def replan(self, plan: Plan, observation: str) -> Plan:
        """Update a plan based on observation."""
        prompt = f"""The current plan encountered an issue:
Goal: {plan.goal}
Current Step: {plan.current_step}
Observation: {observation}

Create a revised plan that addresses this issue. Output JSON."""

        try:
            result = await self.model_manager.complete(prompt)
            plan_data = self._extract_json(result)
            
            if plan_data:
                plan.steps = [
                    PlanStep(
                        step_type=StepType(s.get("step_type", "act")),
                        description=s.get("description", ""),
                        tool=s.get("tool"),
                        args=s.get("args", {}),
                        expected_outcome=s.get("expected_outcome")
                    )
                    for s in plan_data.get("steps", [])
                ]
                plan.current_step = 0
                plan.failed = False
                plan.error = None
            
        except Exception as e:
            logger.error(f"Replanning failed: {e}")
            plan.error = str(e)
            plan.failed = True
        
        return plan
    
    def _extract_json(self, text: str) -> Optional[dict]:
        """Extract JSON from text response."""
        # Try to find JSON block
        for start in ["```json", "```", "{"]:
            if start in text:
                idx = text.index(start)
                text = text[idx:]
                break
        
        for end in ["```", "}"]:
            if end in text:
                idx = text.rindex(end)
                text = text[:idx+1]
                break
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    
    def get_next_step(self, plan: Plan) -> Optional[PlanStep]:
        """Get the next step in a plan."""
        if plan.completed or plan.failed:
            return None
        if plan.current_step < len(plan.steps):
            return plan.steps[plan.current_step]
        return None
    
    def advance_step(self, plan: Plan):
        """Move to the next step."""
        plan.current_step += 1
        if plan.current_step >= len(plan.steps):
            plan.completed = True
