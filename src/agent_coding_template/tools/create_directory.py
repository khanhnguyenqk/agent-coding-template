import os
from typing import Optional, Type, ClassVar
from langchain_core.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from pydantic import BaseModel, Field

class CreateDirectoryToolArgs(BaseModel):
    directory: str = Field(..., description="The path of the directory to create.")

class CreateDirectoryTool(BaseTool):
    """
    A tool to create a new directory at a specified path.

    Usage:
        Provide the directory path. If the directory already exists and exist_ok is False,
        an error message is returned. If exist_ok is True, the function quietly succeeds.
    """
    name: ClassVar[str] = "CreateDirectoryTool"
    description: ClassVar[str] = (
        "Creates a new directory at the specified path."
    )
    args_schema: Type[BaseModel] = CreateDirectoryToolArgs

    def _run(
        self,
        directory: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            os.makedirs(directory, exist_ok=True)
            return f"Successfully created directory '{directory}'."
        except Exception as e:
            return f"Error creating directory: {str(e)}"

    async def _arun(
        self,
        directory: str,
        exist_ok: bool = False,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        sync_manager = run_manager.get_sync() if run_manager else None
        return self._run(directory, exist_ok=exist_ok, run_manager=sync_manager) 