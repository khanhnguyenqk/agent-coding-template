import os
import shutil
from typing import Optional, Type, ClassVar
from langchain_core.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from pydantic import BaseModel, Field

class FileCopyToolArgs(BaseModel):
    source_path: str = Field(..., description="The path of the file to copy from.")
    destination_path: str = Field(..., description="The path where the file should be copied to.")
    overwrite: bool = Field(default=True, description="If false and the destination file exists, the tool will not overwrite the file.")

class FileCopyTool(BaseTool):
    """
    A tool to copy a file from a source path to a destination path.
    """
    name: ClassVar[str] = "FileCopyTool"
    description: ClassVar[str] = (
        "Copies a file from the source path to the destination path. "
        "If the destination file exists, it can be overwritten depending on the 'overwrite' flag."
    )
    args_schema: Type[BaseModel] = FileCopyToolArgs

    def _run(
        self,
        source_path: str,
        destination_path: str,
        overwrite: bool = True,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        # Verify source file exists
        if not os.path.isfile(source_path):
            return f"Error: Source file '{source_path}' does not exist."
        
        # Check if destination exists and handle overwrite flag
        if os.path.exists(destination_path) and not overwrite:
            return f"Error: Destination file '{destination_path}' already exists and overwrite is disabled."
        
        # Create destination directory if not exists.
        dest_dir = os.path.dirname(destination_path)
        if dest_dir and not os.path.exists(dest_dir):
            try:
                os.makedirs(dest_dir, exist_ok=True)
            except Exception as e:
                return f"Error creating destination directory: {str(e)}"
        
        try:
            shutil.copy2(source_path, destination_path)
            return f"Successfully copied file from '{source_path}' to '{destination_path}'."
        except Exception as e:
            return f"Error copying file: {str(e)}"

    async def _arun(
        self,
        source_path: str,
        destination_path: str,
        overwrite: bool = True,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        sync_manager = run_manager.get_sync() if run_manager else None
        return self._run(source_path, destination_path, overwrite, run_manager=sync_manager) 