"""
MCP tools for creating robot schemas and example datasets
"""
import os
from typing import Optional, List

from mcp.server.fastmcp import FastMCP

import aurelian.agents.filesystem.filesystem_tools as fst
from aurelian.agents.robot.robot_ontology_agent import SYSTEM
import aurelian.agents.robot.robot_tools as rt
from aurelian.agents.robot.robot_config import RobotDependencies
from pydantic_ai import RunContext, ModelRetry

# Initialize FastMCP server
mcp = FastMCP("robot", instructions=SYSTEM)



from aurelian.dependencies.workdir import WorkDir

def deps() -> RobotDependencies:
    deps = RobotDependencies()
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/aurelian")
    deps.workdir = WorkDir(loc)
    return deps

def ctx() -> RunContext[RobotDependencies]:
    rc: RunContext[RobotDependencies] = RunContext[RobotDependencies](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.tool()
async def write_and_compile_template(template: str, save_to_file: str= "core.csv", import_ontologies: Optional[List[str]] = None) -> str:
    """
    Adds a template to the file system and compile it to OWL

    Args:
        ctx: context
        template: robot template as string. Do not truncate, always pass the whole template, including header.
        save_to_file: file name to save the templates to. Defaults to core.csv. Only written if file compiles to OWL
        import_ontologies: list of ontologies to import. These should be files in the working directory.

    Returns:
        report
    """
    return await rt.write_and_compile_template(ctx(), template, save_to_file, import_ontologies)


@mcp.tool()
async def inspect_file(data_file: str) -> str:
    """
    Inspect a file in the working directory.

    Args:
        ctx:
        data_file: name of file

    Returns:

    """
    return await fst.inspect_file(ctx(), data_file)


@mcp.tool()
async def list_files() -> str:
    """
    List files in the working directory.

    Args:
        ctx:

    Returns:

    """
    return await fst.list_files(ctx())


@mcp.tool()
async def write_to_file(data: str, file_name: str) -> str:
    """
    Write data to a file in the working directory.

    Args:
        ctx:
        data:
        file_name:

    Returns:

    """
    return await fst.write_to_file(ctx(), file_name, data)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')