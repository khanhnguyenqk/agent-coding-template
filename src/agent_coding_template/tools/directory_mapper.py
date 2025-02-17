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
    show_hidden: bool = Field(
        False, description="Whether to include hidden files and directories in the output."
    )
    depth: Optional[int] = Field(
        None, description="Maximum depth level to traverse, starting from 1. If None, traverse all levels."
    )

class DirectoryMapperTool(BaseTool):
    """
    A tool to map out a given directory's files and folders in a tree structure.
    It now accepts an optional depth parameter (starting at level 1) to limit the depth
    of traversal. Use depth to restrict the output and save tokens when only top-level
    information is needed.

    Usage:
        Provide the directory path along with optional output_format ('ascii' or 'json'),
        show_hidden and depth (starting at 1) to control the recursion depth. The tool returns a string representing the directory tree.
    """
    name: ClassVar[str] = "DirectoryMapperTool"
    description: ClassVar[str] = (
        "Maps out a given directory's files and folders. "
        "Takes in a directory path and options for output format ('ascii' or 'json'), "
        "whether to show hidden entries, and a maximum depth level (depth) for traversal. "
        "Use depth to restrict the output and save tokens when only top-level "
        "information is needed. "
        "Returns a string representing the directory tree."
    )
    args_schema: Type[BaseModel] = DirectoryMapperToolArgs

    def _run(
        self, 
        directory: str, 
        output_format: str = "ascii", 
        show_hidden: bool = False,
        depth: Optional[int] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Synchronously maps out the directory structure.

        Args:
            directory (str): The path of the directory to map.
            output_format (str): The output format, either "ascii" or "json".
            show_hidden (bool): If True, include hidden files and directories.
            depth (Optional[int]): Maximum depth level to traverse. If None, traverse all levels.
            
        Returns:
            str: A string representation of the directory tree.
        """
        if not os.path.isdir(directory):
            return f"Error: The provided path '{directory}' is not a valid directory."

        if output_format.lower() == "json":
            tree = self._build_json_tree(directory, show_hidden=show_hidden, depth=depth, level=1)
            return json.dumps(tree, indent=2)
        else:
            lines = self._build_ascii_tree(directory, prefix="", show_hidden=show_hidden, depth=depth, level=1)
            return "\n".join(lines)

    async def _arun(
        self, 
        directory: str, 
        output_format: str = "ascii", 
        show_hidden: bool = False,
        depth: Optional[int] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """
        Asynchronous version not supported for this tool.
        """
        sync_manager = run_manager.get_sync() if run_manager else None
        return self._run(directory, output_format=output_format, show_hidden=show_hidden, depth=depth, run_manager=sync_manager)

    def _build_ascii_tree(self, path: str, prefix: str = "", show_hidden: bool = False, 
                          depth: Optional[int] = None, level: int = 1) -> List[str]:
        """
        Recursively build an ASCII representation of the directory tree.

        Args:
            path (str): The current directory or file path.
            prefix (str): The prefix for the current level (used for indentation).
            show_hidden (bool): If True, include hidden files and directories.
            depth (Optional[int]): Maximum depth level to traverse.
            level (int): The current recursion depth.
            
        Returns:
            List[str]: A list of strings representing each line of the ASCII tree.
        """
        basename = os.path.basename(path.rstrip(os.sep)) or path
        line = prefix + basename + ("/" if os.path.isdir(path) else "")
        lines = [line]
        if os.path.isdir(path):
            # Stop recursion if the maximum depth has been reached.
            if depth is not None and level >= depth:
                return lines
            try:
                entries = sorted([entry for entry in os.listdir(path) if show_hidden or not entry.startswith(".")])
            except PermissionError:
                lines.append(prefix + "    [Permission Denied]")
                return lines
            count = len(entries)
            for idx, entry in enumerate(entries):
                full_path = os.path.join(path, entry)
                connector = "└── " if idx == count - 1 else "├── "
                new_prefix = prefix + ("    " if idx == count - 1 else "│   ")
                if os.path.isdir(full_path):
                    lines.append(prefix + connector + entry + "/")
                    sub_lines = self._build_ascii_tree(full_path, new_prefix, show_hidden, depth, level + 1)
                    # Skip the redundant directory name from the sub_lines.
                    lines.extend(sub_lines[1:])
                else:
                    lines.append(prefix + connector + entry)
        return lines

    def _build_json_tree(self, path: str, show_hidden: bool = False, 
                         depth: Optional[int] = None, level: int = 1) -> dict:
        """
        Recursively build a JSON representation of the directory tree.

        Args:
            path (str): The current directory or file path.
            show_hidden (bool): If True, include hidden files and directories.
            depth (Optional[int]): Maximum depth level to traverse.
            level (int): The current recursion depth.
            
        Returns:
            dict: A dictionary representing the node in the directory tree.
        """
        basename = os.path.basename(path.rstrip(os.sep)) or path
        if os.path.isdir(path):
            # Stop recursion if the maximum depth has been reached.
            if depth is not None and level >= depth:
                return {
                    "name": basename,
                    "type": "directory",
                    "children": []
                }
            try:
                entries = sorted([entry for entry in os.listdir(path) if show_hidden or not entry.startswith(".")])
            except PermissionError:
                return {
                    "name": basename,
                    "type": "directory",
                    "error": "Permission Denied"
                }
            return {
                "name": basename,
                "type": "directory",
                "children": [self._build_json_tree(os.path.join(path, entry), show_hidden, depth, level+1) for entry in entries]
            }
        else:
            return {
                "name": basename,
                "type": "file"
            }
