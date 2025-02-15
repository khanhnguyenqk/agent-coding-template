import os
import json
from typing import Optional, Type, ClassVar, List
from langchain_core.tools import BaseTool
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from pydantic import BaseModel, Field

class DirectoryMapperToolArgs(BaseModel):
    directory: str = Field(..., description="The path of the directory to map.")
    output_format: Optional[str] = Field(
        "ascii", description="The format of the output. Options are 'ascii' or 'json'."
    )

class DirectoryMapperTool(BaseTool):
    """
    A tool to map out a directory's files and folders in a tree structure.

    Usage:
        Provide the directory path and an optional output format ('ascii' or 'json')
        as input. This tool will return a string representing the directory tree.
    """
    name: ClassVar[str] = "DirectoryMapperTool"
    description: ClassVar[str] = (
        "Maps out a given directory's files and folders. "
        "Takes in a directory path and an optional output format ('ascii' or 'json') as input, "
        "and returns a string representing the directory tree."
    )
    args_schema: Type[BaseModel] = DirectoryMapperToolArgs

    def _run(
        self, 
        directory: str, 
        output_format: str = "ascii", 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Synchronously maps out the directory structure.

        Args:
            directory (str): The path of the directory to map.
            output_format (str): The output format, either "ascii" or "json".

        Returns:
            str: A string representation of the directory tree.
        """
        if not os.path.isdir(directory):
            return f"Error: The provided path '{directory}' is not a valid directory."

        if output_format.lower() == "json":
            tree = self._build_json_tree(directory)
            return json.dumps(tree, indent=2)
        else:
            lines = self._build_ascii_tree(directory)
            return "\n".join(lines)

    async def _arun(
        self, 
        directory: str, 
        output_format: str = "ascii", 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """
        Asynchronous version not supported for this tool.
        """
        sync_manager = run_manager.get_sync() if run_manager else None
        return self._run(directory, output_format=output_format, run_manager=sync_manager)

    def _build_ascii_tree(self, path: str, prefix: str = "") -> List[str]:
        """
        Recursively build an ASCII representation of the directory tree.

        Args:
            path (str): The current directory or file path.
            prefix (str): The prefix for the current level (used for indentation).

        Returns:
            List[str]: A list of strings representing each line of the ASCII tree.
        """
        basename = os.path.basename(path.rstrip(os.sep)) or path
        # Mark directories with a trailing '/'
        line = prefix + basename + ("/" if os.path.isdir(path) else "")
        lines = [line]
        if os.path.isdir(path):
            try:
                entries = sorted(os.listdir(path))
            except PermissionError:
                lines.append(prefix + "    [Permission Denied]")
                return lines
            count = len(entries)
            for idx, entry in enumerate(entries):
                full_path = os.path.join(path, entry)
                connector = "└── " if idx == count - 1 else "├── "
                new_prefix = prefix + ("    " if idx == count - 1 else "│   ")
                if os.path.isdir(full_path):
                    # Append directory entry and recursively build its subtree.
                    lines.append(prefix + connector + entry + "/")
                    # Recursively build the subtree and skip the first line (redundant directory name)
                    sub_lines = self._build_ascii_tree(full_path, new_prefix)
                    lines.extend(sub_lines[1:])
                else:
                    lines.append(prefix + connector + entry)
        return lines

    def _build_json_tree(self, path: str) -> dict:
        """
        Recursively build a JSON representation of the directory tree.

        Args:
            path (str): The current directory or file path.

        Returns:
            dict: A dictionary representing the node in the directory tree.
        """
        basename = os.path.basename(path.rstrip(os.sep)) or path
        if os.path.isdir(path):
            try:
                entries = sorted(os.listdir(path))
            except PermissionError:
                return {
                    "name": basename,
                    "type": "directory",
                    "error": "Permission Denied"
                }
            return {
                "name": basename,
                "type": "directory",
                "children": [self._build_json_tree(os.path.join(path, entry)) for entry in entries]
            }
        else:
            return {
                "name": basename,
                "type": "file"
            }
