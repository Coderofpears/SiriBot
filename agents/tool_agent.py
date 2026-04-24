"""Tool agent - executes tasks using registered tools."""

import logging
from typing import Optional, Any
from dataclasses import dataclass, field
from .reasoning_agent import Plan, PlanStep

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Result of tool execution."""

    success: bool
    output: Any
    error: Optional[str] = None
    tool_name: str = ""


class ToolAgent:
    """Handles tool execution and tool registry management."""

    def __init__(self, tool_registry, safety_manager):
        self.tool_registry = tool_registry
        self.safety_manager = safety_manager
        self.execution_history: list[ToolResult] = []

    async def execute_plan(self, plan: Plan) -> str:
        """Execute a complete plan."""
        results = []
        total_steps = len(plan.steps)
        max_iterations = max(total_steps * 2 + 1, 1)
        iterations = 0

        while not plan.completed and not plan.failed and iterations < max_iterations:
            iterations += 1

            if plan.current_step >= total_steps:
                plan.completed = True
                break

            step = plan.steps[plan.current_step]

            if step.step_type.value == "think":
                logger.info(f"Thinking: {step.description}")
                plan.current_step += 1
                continue

            if step.tool:
                result = await self.execute_tool(step.tool, **step.args)
                self.execution_history.append(result)

                if result.success:
                    results.append(result.output)
                    plan.current_step += 1
                else:
                    plan.error = result.error
                    plan.failed = True
                    results.append(f"Error: {result.error}")
            else:
                plan.current_step += 1

        if plan.failed:
            return f"Plan failed: {plan.error}"

        if not results:
            return "Plan completed but produced no output."

        return "\n".join(str(r) for r in results)

    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a specific tool."""
        logger.info(f"Executing tool: {tool_name}")

        # Check if tool exists
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                output=None,
                error=f"Unknown tool: {tool_name}",
                tool_name=tool_name,
            )

        # Check safety
        if not self.safety_manager.is_safe(tool_name, kwargs):
            return ToolResult(
                success=False,
                output=None,
                error=f"Operation blocked by safety manager: {tool_name}",
                tool_name=tool_name,
            )

        # Request confirmation for risky operations
        if self.safety_manager.needs_confirmation(tool_name, kwargs):
            # For now, auto-confirm. In real impl, would prompt user
            logger.warning(f"Risky operation {tool_name} auto-confirmed")

        try:
            result = await tool(**kwargs)
            return ToolResult(success=True, output=result, tool_name=tool_name)
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return ToolResult(
                success=False, output=None, error=str(e), tool_name=tool_name
            )

    def get_history(self, limit: int = 50) -> list[ToolResult]:
        """Get recent tool execution history."""
        return self.execution_history[-limit:]


class SafetyManager:
    """Manages safety checks for tool execution."""

    RISKY_PATTERNS = [
        ("delete", "Permanently deleting files"),
        ("rm ", "Shell rm command"),
        ("sudo", "Superuser operations"),
        ("format", "Disk formatting"),
        ("dd", "Direct disk operations"),
    ]

    def __init__(self, config):
        self.config = config
        self.confirmation_required_patterns = config.agent.confirmation_required

    def is_safe(self, tool_name: str, args: dict) -> bool:
        """Check if a tool execution is safe."""
        if not self.config.safety.allow_shell_commands:
            if tool_name in ["shell", "bash"]:
                return False

        if not self.config.safety.allow_file_operations:
            if tool_name in ["file_read", "file_write", "file_delete"]:
                return False

        return True

    def needs_confirmation(self, tool_name: str, args: dict) -> bool:
        """Check if a tool execution needs user confirmation."""
        args_str = str(args).lower()

        for pattern in self.confirmation_required_patterns:
            if pattern.lower() in args_str:
                return True

        return False
