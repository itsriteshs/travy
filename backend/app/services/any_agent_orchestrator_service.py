from typing import Any

from app.core.config import settings


class AnyAgentOrchestratorService:
    """Optional any-agent wrapper for MCP-backed orchestration.

    The production request path remains explicit for security and budget checks.
    This service is available when an mcpd streamable MCP endpoint is configured.
    """

    async def run(self, task: str) -> Any:
        from any_agent import AgentConfig, AnyAgent
        from any_agent.config import MCPStreamableHttp

        agent = await AnyAgent.create_async(
            "tinyagent",
            AgentConfig(
                model_id=settings.ANY_AGENT_MODEL_ID,
                api_base=settings.LLAMAFILE_BASE_URL,
                api_key=settings.LLAMAFILE_API_KEY or "not-needed",
                instructions=(
                    "Use MCP tools for factual travel data. Do not invent places or itineraries. "
                    "Final itinerary generation must be delegated to Otari only."
                ),
                tools=[MCPStreamableHttp(url=settings.TRAVY_MCP_STREAMABLE_URL)],
                model_args={"temperature": 0},
            ),
        )
        try:
            return await agent.run_async(task)
        finally:
            await agent.cleanup_async()
