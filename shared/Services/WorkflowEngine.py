"""Autonomous workflow engine for self-directed task execution."""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowTrigger(Enum):
    SCHEDULE = "schedule"
    EVENT = "event"
    CONDITION = "condition"
    MANUAL = "manual"


@dataclass
class WorkflowStep:
    """A single step in an autonomous workflow."""

    name: str
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 60.0
    condition: Optional[str] = None


@dataclass
class Workflow:
    """An autonomous workflow definition."""

    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    trigger: WorkflowTrigger = WorkflowTrigger.MANUAL
    trigger_config: Dict[str, Any] = field(default_factory=dict)
    state: WorkflowState = WorkflowState.IDLE
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0


class WorkflowEngine:
    """Engine for autonomous workflow execution."""

    def __init__(self, orchestrator, config: Optional[Dict] = None):
        self.orchestrator = orchestrator
        self.config = config or {}
        self.workflows: Dict[str, Workflow] = {}
        self.active_workflow: Optional[Workflow] = None
        self._running_task: Optional[asyncio.Task] = None
        self._event_listeners: Dict[str, List[callable]] = {}
        self._condition_checkers: Dict[str, Callable] = {}
        logger.info("WorkflowEngine initialized")

    def register_workflow(self, workflow: Workflow):
        """Register a workflow."""
        self.workflows[workflow.id] = workflow
        logger.info(f"Registered workflow: {workflow.name}")

    def unregister_workflow(self, workflow_id: str):
        """Unregister a workflow."""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            logger.info(f"Unregistered workflow: {workflow_id}")

    async def execute_workflow(
        self, workflow_id: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute a workflow autonomously."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"success": False, "error": f"Workflow not found: {workflow_id}"}

        if workflow.state == WorkflowState.RUNNING:
            return {"success": False, "error": "Workflow already running"}

        workflow.state = WorkflowState.RUNNING
        workflow.last_run = datetime.now()
        workflow.run_count += 1
        self.active_workflow = workflow

        context = context or {}
        results = []

        logger.info(f"Starting autonomous workflow: {workflow.name}")

        try:
            for i, step in enumerate(workflow.steps):
                result = await self._execute_step(step, context, results)
                results.append(result)

                if not result["success"]:
                    if step.retry_count < step.max_retries:
                        step.retry_count += 1
                        logger.warning(
                            f"Retrying step {step.name} (attempt {step.retry_count})"
                        )
                        continue
                    else:
                        workflow.state = WorkflowState.FAILED
                        break

                if step.condition and not await self._evaluate_condition(
                    step.condition, context, results
                ):
                    logger.info(f"Skipping step {step.name} - condition not met")
                    continue

            workflow.state = WorkflowState.COMPLETED
            workflow.success_count += 1

            return {
                "success": True,
                "workflow_id": workflow_id,
                "steps_completed": len([r for r in results if r["success"]]),
                "results": results,
            }

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            workflow.state = WorkflowState.FAILED
            return {"success": False, "error": str(e), "results": results}

        finally:
            self.active_workflow = None

    async def _execute_step(
        self, step: WorkflowStep, context: Dict, results: List
    ) -> Dict[str, Any]:
        """Execute a single workflow step."""
        logger.info(f"Executing step: {step.name}")

        try:
            if step.action == "chat":
                response = await self.orchestrator.chat(step.params.get("message", ""))
                return {"success": True, "step": step.name, "output": response}

            elif step.action == "tool":
                tool_name = step.params.get("tool")
                tool_args = step.params.get("args", {})
                result = await self.orchestrator.tool_agent.execute_tool(
                    tool_name, **tool_args
                )
                return {
                    "success": result.success,
                    "step": step.name,
                    "output": result.output,
                    "error": result.error,
                }

            elif step.action == "wait":
                await asyncio.sleep(step.params.get("seconds", 1))
                return {"success": True, "step": step.name}

            elif step.action == "notify":
                logger.info(f"Notification: {step.params.get('message', '')}")
                return {"success": True, "step": step.name}

            elif step.action == "branch":
                condition = step.params.get("condition")
                if condition and await self._evaluate_condition(
                    condition, context, results
                ):
                    return {"success": True, "step": step.name, "branch_taken": True}
                return {"success": True, "step": step.name, "branch_taken": False}

            else:
                return {
                    "success": False,
                    "step": step.name,
                    "error": f"Unknown action: {step.action}",
                }

        except asyncio.TimeoutError:
            return {"success": False, "step": step.name, "error": "Step timed out"}
        except Exception as e:
            return {"success": False, "step": step.name, "error": str(e)}

    async def _evaluate_condition(
        self, condition: str, context: Dict, results: List
    ) -> bool:
        """Evaluate a condition expression."""
        try:
            for key, checker in self._condition_checkers.items():
                if key in condition:
                    condition = condition.replace(key, str(checker(context, results)))
            return eval(condition, {"__builtins__": {}}, {})
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False

    def register_condition_checker(self, name: str, checker: Callable):
        """Register a custom condition checker."""
        self._condition_checkers[name] = checker

    def register_event_listener(self, event: str, callback: callable):
        """Register an event listener."""
        if event not in self._event_listeners:
            self._event_listeners[event] = []
        self._event_listeners[event].append(callback)

    async def trigger_event(self, event: str, data: Dict):
        """Trigger an event that may start workflows."""
        logger.info(f"Event triggered: {event}")

        for workflow in self.workflows.values():
            if workflow.trigger == WorkflowTrigger.EVENT:
                if workflow.trigger_config.get("event") == event:
                    asyncio.create_task(self.execute_workflow(workflow.id, data))

        if event in self._event_listeners:
            for listener in self._event_listeners[event]:
                await listener(data)

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {}

        return {
            "id": workflow.id,
            "name": workflow.name,
            "state": workflow.state.value,
            "run_count": workflow.run_count,
            "success_rate": workflow.success_count / max(1, workflow.run_count),
            "last_run": workflow.last_run.isoformat() if workflow.last_run else None,
        }

    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows."""
        return [self.get_workflow_status(w.id) for w in self.workflows.values()]


def create_example_workflow() -> Workflow:
    """Create an example autonomous workflow."""
    return Workflow(
        id="daily_report",
        name="Daily Summary Report",
        description="Generate and send daily summary",
        steps=[
            WorkflowStep(
                name="collect_data",
                action="tool",
                params={"tool": "shell", "args": {"command": "date"}},
            ),
            WorkflowStep(
                name="generate_report",
                action="chat",
                params={"message": "Create a summary of today's tasks"},
            ),
            WorkflowStep(
                name="save_report",
                action="tool",
                params={
                    "tool": "file_write",
                    "args": {
                        "path": "~/siribot_reports/report.md",
                        "content": "{{generate_report.output}}",
                    },
                },
            ),
        ],
        trigger=WorkflowTrigger.SCHEDULE,
        trigger_config={"cron": "0 9 * * *"},
    )
