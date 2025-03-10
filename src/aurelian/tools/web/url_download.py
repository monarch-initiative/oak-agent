from dataclasses import dataclass

from pydantic import TypeAdapter
from pydantic_ai.tools import Tool
from typing_extensions import TypedDict

from aurelian.dependencies.workdir import WorkDir


__all__ = ["download_url_tool"]

class URLDownloadResult(TypedDict):
    """The result of downloading a URL."""

    size: int
    """The size of the downloaded content."""
    location: str
    """The location of the downloaded content."""

ta = TypeAdapter(list[URLDownloadResult])

@dataclass
class URLDownloadTool:
    """A tool for downloading a URL."""
    workdir: WorkDir

    async def __call__(self, url:str, local_file_name: str) -> list[dict]:
        """Download the contents of a URL.

        Args:
            url: URL of the web page
            local_file_name: Name of the local file to save

        Returns:
            The contents of the web page.
        """
        import asyncio
        import aurelian.utils.search_utils as su
        data = await asyncio.to_thread(su.retrieve_web_page, url)
        self.workdir.write_file(local_file_name, data)
        return ta.validate_python([{"location": local_file_name, "size": len(data)}])

def download_url_tool(workdir: WorkDir):
    """Create a URL download tool."""
    udt = URLDownloadTool(workdir=workdir)
    c = udt.__call__
    return Tool(
        udt.__call__,
        name="download_web_page",
        description="Download the contents of a URL.",
    )