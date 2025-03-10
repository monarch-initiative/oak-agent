"""
MCP integration for the UniProt agent.
"""
import json
import os
from typing import Dict, Any, List, Optional

from anthropic import Anthropic
from pydantic_ai import Agent

# Import directly from the MCP module
from .uniprot_agent import uniprot_agent, UNIPROT_SYSTEM_PROMPT
from .uniprot_config import UniprotConfig, get_config


def tools_to_anthropic_tools(agent: Agent) -> List[Dict[str, Any]]:
    """Convert pydantic-ai Agent tools to Anthropic tools format.
    
    Args:
        agent: The pydantic-ai Agent with tools
        
    Returns:
        A list of tools in the Anthropic format
    """
    anthropic_tools = []
    for tool in agent.tools:
        anthropic_tool = {
            "name": tool.name,
            "description": tool.description,
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        
        for param_name, param in tool.params.items():
            if param_name == "ctx":
                continue
                
            param_schema = {"type": "string"}
            if param.annotation.__origin__ == list:
                param_schema = {
                    "type": "array",
                    "items": {"type": "string"}
                }
                
            anthropic_tool["input_schema"]["properties"][param_name] = param_schema
            if param.default == param.empty:
                anthropic_tool["input_schema"]["required"].append(param_name)
                
        anthropic_tools.append(anthropic_tool)
        
    return anthropic_tools


def create_bedrock_compatible_resp(
    response_id: str, 
    model: str, 
    role: str, 
    content: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Create a response compatible with the Bedrock format.
    
    Args:
        response_id: The response ID
        model: The model name
        role: The role (usually 'assistant')
        content: The content from the Anthropic response
        
    Returns:
        A response in the Bedrock format
    """
    return {
        "id": response_id,
        "model": model,
        "choices": [
            {
                "message": {
                    "role": role,
                    "content": content
                }
            }
        ]
    }


def get_uniprot_mcp_tools() -> List[Dict[str, Any]]:
    """Get the MCP tools for the UniProt agent.

    Returns:
        A list of tools in the MCP format
    """
    return tools_to_anthropic_tools(uniprot_agent)


def get_uniprot_mcp_messages(
    messages: Optional[List[Dict[str, Any]]] = None,
    system: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get MCP messages for the UniProt agent.

    Args:
        messages: Previous messages
        system: System message override

    Returns:
        List of MCP messages
    """
    if messages is None:
        messages = []
    
    if system is None:
        system = UNIPROT_SYSTEM_PROMPT
    
    if not messages or messages[0].get("role") != "system":
        messages = [{"role": "system", "content": system}] + messages
    
    return messages


def handle_uniprot_mcp_request(
    messages: List[Dict[str, Any]],
    config: Optional[UniprotConfig] = None,
    model: str = "claude-3-5-sonnet-20240620",
    max_tokens: int = 4096,
    temperature: float = 0.0,
) -> Dict[str, Any]:
    """Handle an MCP request for the UniProt agent.

    Args:
        messages: The messages from the client
        config: The UniProt configuration (optional)
        model: The model to use
        max_tokens: The maximum number of tokens to generate
        temperature: The temperature to use for generation

    Returns:
        An MCP response
    """
    config = config or get_config()
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required for MCP")

    client = Anthropic(api_key=api_key)
    
    # Prepare the messages and tools
    mcp_messages = get_uniprot_mcp_messages(messages)
    mcp_tools = get_uniprot_mcp_tools()
    
    # Send the request to Anthropic
    response = client.messages.create(
        model=model,
        messages=mcp_messages,
        tools=mcp_tools,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    # Return the response in a format compatible with the MCP protocol
    return create_bedrock_compatible_resp(
        response_id=response.id,
        model=model,
        role="assistant",
        content=response.content,
    )