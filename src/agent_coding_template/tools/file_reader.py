import os
from typing import Optional, Type, ClassVar
from langchain_core.tools import BaseTool
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from pydantic import BaseModel, Field

class FileReaderToolArgs(BaseModel):
    file_path: str = Field(..., description="The path of the file to read.")
    max_chars: Optional[int] = Field(
        None, description="Optional limit on the number of characters to read from the file."
    )

class FileReaderTool(BaseTool):
    """
    A tool to read the contents of a file.

    Usage:
        Provide the file path (and optionally a maximum character limit) as input.
        This tool will return the contents of the file as a string.
    """
    name: ClassVar[str] = "FileReaderTool"
    description: ClassVar[str] = (
        "Reads the contents of a file given its path. "
        "Takes in a file path and returns the file contents as a string. "
        "Optionally, a maximum number of characters to read can be specified."
    )
    args_schema: Type[BaseModel] = FileReaderToolArgs

    def _run(
        self, 
        file_path: str, 
        max_chars: Optional[int] = None, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Synchronously reads the file contents.

        Args:
            file_path (str): The path of the file to read.
            max_chars (Optional[int]): Maximum number of characters to read from the file.

        Returns:
            str: The contents of the file, or an error message if the file could not be read.
        """
        if not os.path.isfile(file_path):
            return f"Error: The provided path '{file_path}' is not a valid file."
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if max_chars is not None:
                    content = content[:max_chars]
                return content
        except Exception as e:
            return f"Error reading file: {str(e)}"

    async def _arun(
        self, 
        file_path: str, 
        max_chars: Optional[int] = None, 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """
        Asynchronous version not supported for this tool.
        """
        sync_manager = run_manager.get_sync() if run_manager else None
        return self._run(file_path, max_chars=max_chars, run_manager=sync_manager)
