import re
from typing import Any

import httpx
from pydantic import BaseModel
from pydantic_ai import RunContext

from aurelian.dependencies.workdir import WorkDir, HasWorkdir


class DownloadResult(BaseModel):
    file_name: str
    num_lines: int

async def inspect_file(ctx: RunContext[HasWorkdir], data_file: str) -> str:
    """
    Inspect a file in the working directory.

    Args:
        ctx:
        data_file: name of file

    Returns:

    """
    print(f"Inspecting file: {data_file}")
    return ctx.deps.workdir.read_file(data_file)


async def download_url_as_markdown(ctx: RunContext[HasWorkdir], url: str, local_file_name: str) -> DownloadResult:
    """
    Download contents of a web page.

    Args:
        ctx: context
        url: URL of the web page
        local_file_name: Name of the local file to save the

    Returns:
        DownloadResult: information about the downloaded file
    """
    workdir: WorkDir = ctx.deps.workdir
    from markdownify import markdownify

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=20.0)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Convert the HTML content to Markdown
        markdown_content = markdownify(response.text).strip()

        # Remove multiple line breaks
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

        # Assuming write_file is also async
        workdir.write_file(local_file_name, markdown_content)

        return DownloadResult(file_name=local_file_name, num_lines=len(markdown_content.split("\n")))


async def list_files(ctx: RunContext[HasWorkdir]) -> str:
    """
    List files in the working directory.

    Args:
        ctx:

    Returns:

    """
    return "\n".join(ctx.deps.workdir.list_file_names())


async def write_to_file(ctx: RunContext[HasWorkdir], file_name: str, data: str) -> str:
    """
    Write data to a file in the working directory.

    Args:
        ctx:
        file_name:
        data:

    Returns:

    """
    print(f"Writing data to file: {file_name}")
    ctx.deps.workdir.write_file(file_name, data)
    return f"Data written to {file_name}"


async def show_local_files(ctx: RunContext[HasWorkdir]) -> str:
    file_names = ctx.deps.workdir.list_file_names()
    if file_names:
        return f"Local files: {file_names}"
    return "No files currently in the working directory"
