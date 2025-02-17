import pytest
from pathlib import Path
from agent_coding_template.tools.file_editor import FileEditorTool

@pytest.fixture
def temp_file(tmp_path: Path):
    # Create a sample file with three lines.
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Line1\nLine2\nLine3\n", encoding="utf-8")
    return str(file_path)

def test_new_file_success(tmp_path: Path):
    file_path = tmp_path / "newfile.txt"
    tool = FileEditorTool()
    result = tool._run(str(file_path), action="new", content="New file content.")
    assert "Successfully created new file" in result
    # Verify the content of the new file.
    written = file_path.read_text(encoding="utf-8")
    assert written == "New file content."

def test_new_file_already_exists(temp_file: str):
    tool = FileEditorTool()
    result = tool._run(temp_file, action="new", content="Should not overwrite.")
    assert "already exists" in result

def test_insert_with_line_number(temp_file: str):
    tool = FileEditorTool()
    # Insert content before line 2.
    result = tool._run(temp_file, action="insert", content="Inserted\n", start_line=2)
    assert "Successfully inserted content" in result
    updated_content = open(temp_file, encoding="utf-8").read()
    # Expected file content:
    # Line1\nInserted\nLine2\nLine3\n
    expected = "Line1\nInserted\nLine2\nLine3\n"
    assert updated_content == expected

def test_insert_appending(tmp_path: Path):
    # Create a file with two lines.
    file_path = tmp_path / "append.txt"
    file_path.write_text("First line\nSecond line\n", encoding="utf-8")
    tool = FileEditorTool()
    # Insert without specifying start_line (should append at the end)
    result = tool._run(str(file_path), action="insert", content="Appended")
    assert "Successfully inserted content" in result
    updated_content = file_path.read_text(encoding="utf-8")
    # Since "Appended" does not include a newline, the file will end with "Appended" appended.
    expected = "First line\nSecond line\nAppended"
    assert updated_content == expected

def test_update_content(temp_file: str):
    tool = FileEditorTool()
    # Update line 2 only.
    result = tool._run(temp_file, action="update", content="Updated Line2\n", start_line=2, end_line=2)
    assert "Successfully updated lines 2 to 2" in result
    updated_content = open(temp_file, encoding="utf-8").read()
    # Expected file: Line1\nUpdated Line2\nLine3\n
    expected = "Line1\nUpdated Line2\nLine3\n"
    assert updated_content == expected

def test_update_multiple_lines(temp_file: str):
    tool = FileEditorTool()
    # Update lines 1 to 2 with two new lines.
    new_content = "New Line1\nNew Line2\n"
    result = tool._run(temp_file, action="update", content=new_content, start_line=1, end_line=2)
    assert "Successfully updated lines 1 to 2" in result
    updated_content = open(temp_file, encoding="utf-8").read()
    # Expected file: New Line1\nNew Line2\nLine3\n
    expected = "New Line1\nNew Line2\nLine3\n"
    assert updated_content == expected

def test_update_invalid_range(temp_file: str):
    tool = FileEditorTool()
    # Try to update lines with end_line beyond file length.
    result = tool._run(temp_file, action="update", content="Update\n", start_line=2, end_line=5)
    assert "exceeds total number of lines" in result

def test_invalid_action(temp_file: str):
    tool = FileEditorTool()
    result = tool._run(temp_file, action="delete", content="irrelevant")
    assert "Invalid action" in result

def test_insert_appending_no_newline(tmp_path: Path):
    # Create a file without a trailing newline.
    file_path = tmp_path / "no_newline.txt"
    file_path.write_text("Line1", encoding="utf-8")
    tool = FileEditorTool()
    result = tool._run(str(file_path), action="insert", content="Appended")
    updated_content = file_path.read_text(encoding="utf-8")
    # Expected content should have a newline added between "Line1" and "Appended"
    expected = "Line1\nAppended"
    assert updated_content == expected

def test_new_file_empty_content(tmp_path):
    file_path = tmp_path / "emptyfile.txt"
    tool = FileEditorTool()
    # Pass content as None for new action.
    result = tool._run(str(file_path), action="new", content=None)
    assert "Successfully created new file" in result
    # Verify that the file exists and is empty.
    written = file_path.read_text(encoding="utf-8")
    assert written == ""

def test_insert_with_no_content_error(tmp_path):
    # Create a file first.
    file_path = tmp_path / "insertfile.txt"
    file_path.write_text("Line1\nLine2\n", encoding="utf-8")
    tool = FileEditorTool()
    # Passing None for content on an insert should return an error.
    result = tool._run(str(file_path), action="insert", content=None, start_line=2)
    assert "Error: content is required" in result 