import os
from typing import Optional, Type, ClassVar
from langchain_core.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from pydantic import BaseModel, Field, model_validator

class FileEditorToolArgs(BaseModel):
    file_path: str = Field(..., description="The path of the file to edit.")
    action: str = Field(..., description="The action to perform on the file: 'insert', 'update', or 'new'.")
    content: Optional[str] = Field(
        None, 
        description="REQUIRED for insert/update actions. Content to add. For 'new', creates empty file if omitted."
    )
    start_line: Optional[int] = Field(
        None,
        description=("For 'insert': the line number before which new content will be inserted. "
                     "If not provided, content is appended at the end. "
                     "For 'update': the first line number to update.")
    )
    end_line: Optional[int] = Field(
        None,
        description="For 'update' action: the last line number (inclusive) to be replaced with the new content."
    )

    @model_validator(mode='after')
    def validate_content_requirements(self):
        if self.action in ['insert', 'update'] and self.content is None:
            raise ValueError("'content' is required for insert and update actions")
        if self.action == 'update' and (self.start_line is None or self.end_line is None):
            raise ValueError("Both start_line and end_line are required for update actions")
        return self

class FileEditorTool(BaseTool):
    """
    A tool to edit a file by performing one of three actions:
    1. new: Create a new file with the provided content (fails if file exists).
    2. insert: Insert content into an existing file at a given line number (or append if none provided).
    3. update: Replace lines (from start_line to end_line inclusive) with the provided content.
    """
    name: ClassVar[str] = "FileEditorTool"
    description: ClassVar[str] = (
        "Edits files using one of these strict action patterns:\n"
        "1. new: Create NEW file with content (fails if exists). "
        "Content optional (creates empty file)\n"
        "2. insert: REQUIRES CONTENT. Insert into existing file. "
        "start_line: insert before this line (omit to append)\n"
        "3. update: REQUIRES CONTENT + start_line + end_line. "
        "Replace specified line range in existing file."
        "\nExamples:\n"
        "- To create new file: action='new', file_path='foo.txt'\n"
        "- To insert code: action='insert', file_path='foo.py', content='print(...)'\n"
        "- To update lines 5-10: action='update', file_path='bar.py', "
        "content='new code', start_line=5, end_line=10"
    )
    args_schema: Type[BaseModel] = FileEditorToolArgs

    def _run(
        self,
        file_path: str,
        action: str,
        content: Optional[str] = None,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        if action not in ("new", "insert", "update"):
            return "Error: Invalid action specified. Must be 'new', 'insert', or 'update'."
        try:
            if action == "new":
                if os.path.exists(file_path):
                    return f"Error: File '{file_path}' already exists."
                # Create directories if needed.
                directory = os.path.dirname(file_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                # For new action, if content is None, create an empty file.
                if content is None:
                    content = ""
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"Successfully created new file '{file_path}'."
            else:
                if not os.path.isfile(file_path):
                    return f"Error: File '{file_path}' does not exist."
                # For insert/update, content must not be None.
                if content is None:
                    return "Error: content is required for insert and update actions."
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                if action == "insert":
                    # If a start_line is provided, validate; otherwise, we append.
                    if start_line is not None:
                        if start_line < 1:
                            return "Error: start_line must be at least 1."
                        index = start_line - 1
                        if index > len(lines):
                            index = len(lines)
                    else:
                        index = len(lines)  # append at end
                    # Split the new content into lines, preserving newline characters if present.
                    new_lines = content.splitlines(keepends=True)
                    # If appending and the file does not end with a newline, add one before the new contents.
                    if start_line is None and lines and not lines[-1].endswith("\n") and new_lines:
                        lines[-1] = lines[-1] + "\n"
                    updated_lines = lines[:index] + new_lines + lines[index:]
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(updated_lines)
                    return f"Successfully inserted content into file '{file_path}' at line {index+1}."

                elif action == "update":
                    if start_line is None or end_line is None:
                        return "Error: start_line and end_line are required for update action."
                    if start_line < 1 or end_line < start_line:
                        return "Error: Invalid start_line or end_line values."
                    if end_line > len(lines):
                        return (f"Error: end_line {end_line} exceeds total number of lines in file "
                                f"(file has {len(lines)} lines).")
                    # Replace lines from start_line-1 to end_line.
                    new_lines = content.splitlines(keepends=True)
                    updated_lines = lines[:start_line - 1] + new_lines + lines[end_line:]
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(updated_lines)
                    return f"Successfully updated lines {start_line} to {end_line} in file '{file_path}'."
        except Exception as e:
            return f"Error editing file: {str(e)}"

    async def _arun(
        self,
        file_path: str,
        action: str,
        content: Optional[str] = None,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        sync_manager = run_manager.get_sync() if run_manager else None
        return self._run(file_path, action, content, start_line, end_line, run_manager=sync_manager) 