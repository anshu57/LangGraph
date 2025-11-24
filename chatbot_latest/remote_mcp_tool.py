import asyncio
from typing import List, Any
from langchain_core.tools import StructuredTool
from mcp_client import MCPClient

class RemoteMCPTools:
    """Wrapper for MCP tools as LangChain StructuredTools."""
    
    def __init__(self):
        """Initialize with an MCP client."""
        mcp_servers_config = [{"name": "github", "url": "https://api.github.com/mcp", "headers": {"Authorization": "Bearer TOKEN"}}]
        self.mcp_client = MCPClient(mcp_servers_config)
    
    def _make_langchain_tool(self, mcp_tool) -> StructuredTool:
        """Convert MCP tool to LangChain tool."""
        tool_name = mcp_tool.name
        tool_description = mcp_tool.description or "MCP tool"
        
        async def run_tool(query: str) -> str:
            """Run the MCP tool."""
            try:
                result = await self.mcp_client.run_tool(mcp_tool, {"query": query})
                return result
            except Exception as e:
                return f"Error: {e}"
        
        return StructuredTool.from_function(
            func=sync_run_tool,
            coroutine=run_tool,
            name=tool_name,
            description=tool_description
        )
    
    async def load_tools(self) -> List[StructuredTool]:
        """Load all MCP tools and convert them to LangChain tools."""
        try:
            # Get raw MCP tools
            mcp_tools = await self.mcp_client.get_tools()
            
            # Convert to LangChain tools
            langchain_tools = []
            for mcp_tool in mcp_tools:
                lc_tool = self._make_langchain_tool(mcp_tool)
                langchain_tools.append(lc_tool)
            return langchain_tools
     
        except Exception as e:
            print(f"Failed to load tools: {e}")
            return []