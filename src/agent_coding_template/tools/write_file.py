import os
from typing import Optional, Type, ClassVar
from langchain_core.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from pydantic import BaseModel, Field

class WriteFileToolArgs(BaseModel):
    file_path: str = Field(..., description="The path of the file to write to.")
    content: str = Field(..., description="The content to write to the file.")
    overwrite: bool = Field(
        default=True, description="If False and the file already exists, the tool will not overwrite the file."
    )

class WriteFileTool(BaseTool):
    """
    A tool to write content to a file.

    Usage:
        Provide the file path, the content to write, and optionally whether to overwrite an existing file.
        This tool writes the provided content to the specified file path. It can be used for any file type
        (e.g., Python, Markdown, JSON, config files, etc.).
    """
    name: ClassVar[str] = "WriteFileTool"
    description: ClassVar[str] = (
        "Writes content to a specified file. Supports any file type (e.g., python, markdown, config, json). "
        "If the file already exists, it will be overwritten unless 'overwrite' is set to False."
    )
    args_schema: Type[BaseModel] = WriteFileToolArgs

    def _run(
        self,
        file_path: str,
        content: str,
        overwrite: bool = True,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        # Check if the file exists and overwrite is disabled.
        if os.path.exists(file_path) and not overwrite:
            return f"Error: File '{file_path}' already exists and overwrite is disabled."
        # Create directories if they do not exist.
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                return f"Error creating directories for file: {str(e)}"
        try:
            mode = "w" if overwrite else "x"
            with open(file_path, mode, encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to file '{file_path}'."
        except Exception as e:
            return f"Error writing file: {str(e)}"

    async def _arun(
        self,
        file_path: str,
        content: str,
        overwrite: bool = True,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        sync_manager = run_manager.get_sync() if run_manager else None
        return self._run(file_path, content, overwrite=overwrite, run_manager=sync_manager) 