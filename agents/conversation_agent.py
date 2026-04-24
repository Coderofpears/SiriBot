"""Conversation agent - handles natural language interaction."""

import logging
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class Intent(Enum):
    """User intent classification."""

    CHAT = "chat"
    TASK = "task"
    QUESTION = "question"
    COMMAND = "command"
    UNKNOWN = "unknown"


@dataclass
class Message:
    """Chat message."""

    role: str
    content: str
    metadata: dict = field(default_factory=dict)


@dataclass
class ConversationTurn:
    """A single conversation turn."""

    user_message: str
    intent: Intent
    agent_response: str = ""
    tools_used: list[str] = field(default_factory=list)
    success: bool = True


class ConversationAgent:
    """Handles conversation flow and intent routing."""

    SYSTEM_PROMPT = """You are SiriBot, an intelligent AI assistant that helps users control their computer.

You can:
- Answer questions and have conversations
- Execute tasks using tools
- Plan and execute multi-step workflows
- Access files, apps, and system functions

Be helpful, concise, and proactive. When a task requires multiple steps, plan them out.

Always confirm before executing risky operations like deletions or system changes."""

    def __init__(self, model_manager, memory_agent, tool_agent, reasoning_agent):
        self.model_manager = model_manager
        self.memory_agent = memory_agent
        self.tool_agent = tool_agent
        self.reasoning_agent = reasoning_agent
        self.conversation_history: list[Message] = [
            Message(role="system", content=self.SYSTEM_PROMPT)
        ]

    async def chat(self, user_input: str) -> str:
        """Process a user message and return response."""
        logger.info(f"Processing: {user_input}")

        # Classify intent
        intent = await self._classify_intent(user_input)
        logger.debug(f"Classified intent: {intent}")

        # Route based on intent
        if intent == Intent.TASK:
            response = await self._handle_task(user_input)
        elif intent == Intent.COMMAND:
            response = await self._handle_command(user_input)
        else:
            response = await self._handle_conversation(user_input)

        # Save to memory
        await self.memory_agent.add_interaction(user_input, response, str(intent))

        return response

    async def _classify_intent(self, user_input: str) -> Intent:
        """Classify user intent using the model."""
        prompt = f"""Classify this user input into one of these intents:
- CHAT: Casual conversation or greetings
- TASK: Request to do something (open app, create file, etc.)
- QUESTION: Asking for information
- COMMAND: Direct system command

Input: "{user_input}"

Respond with just the intent name."""

        try:
            result = await self.model_manager.complete(prompt)
            intent_str = result.strip().upper()
            if intent_str in Intent.__members__:
                return Intent[intent_str]
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")

        return Intent.UNKNOWN

    async def _handle_task(self, user_input: str) -> str:
        """Handle task-oriented input."""
        self.conversation_history.append(Message(role="user", content=user_input))

        plan = await self.reasoning_agent.create_plan(user_input)

        if not plan or not plan.steps:
            self.conversation_history.append(
                Message(
                    role="assistant",
                    content="I couldn't understand the task. Could you rephrase?",
                )
            )
            return "I couldn't understand the task. Could you rephrase?"

        result = await self.tool_agent.execute_plan(plan)

        self.conversation_history.append(Message(role="assistant", content=str(result)))

        return str(result)

    async def _handle_command(self, user_input: str) -> str:
        """Handle direct commands."""
        self.conversation_history.append(Message(role="user", content=user_input))

        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        messages.extend(
            [{"role": m.role, "content": m.content} for m in self.conversation_history]
        )

        response = ""
        async for chunk in self.model_manager.generate(messages):
            response += chunk

        self.conversation_history.append(Message(role="assistant", content=response))

        return response

    async def _handle_conversation(self, user_input: str) -> str:
        """Handle general conversation."""
        self.conversation_history.append(Message(role="user", content=user_input))

        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        messages.extend(
            [{"role": m.role, "content": m.content} for m in self.conversation_history]
        )

        response = ""
        async for chunk in self.model_manager.generate(messages):
            response += chunk

        self.conversation_history.append(Message(role="assistant", content=response))

        return response

    def get_history(self, limit: int = 50) -> list[Message]:
        """Get recent conversation history."""
        return self.conversation_history[-limit:]

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = [Message(role="system", content=self.SYSTEM_PROMPT)]
