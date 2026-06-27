import logging
from typing import Any, Dict

import httpx

from app.core.config import settings

logger = logging.getLogger("travy.mcpd_client")


class McpdClient:
    """HTTP client for mcpd-managed MCP tool calls."""

    def __init__(self, server_name: str = "travy"):
        self.base_url = settings.MCPD_BASE_URL.rstrip("/")
        self.server_name = server_name
        self.enabled = bool(self.base_url)

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("MCPD_BASE_URL is not configured")
        url = f"{self.base_url}/api/v1/servers/{self.server_name}/tools/{tool_name}"
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(url, json=arguments)
            response.raise_for_status()
        return response.json()
