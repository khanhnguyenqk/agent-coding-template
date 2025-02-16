import os
from typing import Optional, Type, ClassVar
from langchain_core.tools import BaseTool
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from pydantic import BaseModel, Field

class ReadmeReaderToolArgs(BaseModel):
    directory: str = Field(..., description="The path of the directory where the README.md file is located.")
    max_chars: Optional[int] = Field(
        None, description="Optional limit on the number of characters to read from the README file."
    )

class ReadmeReaderTool(BaseTool):
    """
    A tool to search for and read the README.md file directly from a given directory.

    Usage:
        Provide the directory path where the README.md file resides. Optionally, provide a maximum character limit.
        This tool will return the contents of the README.md file as a string.
    """
    name: ClassVar[str] = "ReadmeReaderTool"
    description: ClassVar[str] = (
        "Searches for and reads the README.md file from the specified directory. "
        "This tool only reads the README.md file without mapping the entire directory to save tokens."
    )
    args_schema: Type[BaseModel] = ReadmeReaderToolArgs

    def _run(
        self, 
        directory: str, 
        max_chars: Optional[int] = None, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        if not os.path.isdir(directory):
            return f"Error: The provided path '{directory}' is not a valid directory."
        readme_path = os.path.join(directory, "README.md")
        if not os.path.isfile(readme_path):
            return f"Error: README.md not found in directory '{directory}'."
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
                if max_chars is not None:
                    content = content[:max_chars]
                return content
        except Exception as e:
            return f"Error reading README.md: {str(e)}"

    async def _arun(
        self, 
        directory: str, 
        max_chars: Optional[int] = None, 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        sync_manager = run_manager.get_sync() if run_manager else None
        return self._run(directory, max_chars=max_chars, run_manager=sync_manager) 