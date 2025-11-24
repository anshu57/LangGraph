import asyncio
from typing import List, Dict, Any
from langchain_mcp_adapters.client import MultiServerMCPClient

class MCPClient:
    
    def __init__(self, config: dict):
        """Initialize the MCP client with server configuration."""
        self.client = MultiServerMCPClient(config)
    
    async def get_tools(self) -> List[Any]:
        """Get all available tools from MCP servers."""
        try:
            tools = await self.client.get_tools()
            return tools
        except Exception as e:
            print(f"Error getting tools: {e}")
            return []
    
    async def run_tool(self, tool, args: Dict[str, Any]) -> str:
        """Run a tool with given arguments."""
        try:
            result = await tool.ainvoke(args)
            return str(result)
        except Exception as e:
            return f"Error: {e}"