import os
import pytest
from pathlib import Path
from agent_coding_template.tools.file_rename import FileRenameTool

@pytest.fixture
def sample_file(tmp_path: Path):
    # Create a sample file to rename.
    source = tmp_path / "original.txt"
    content = "Content for rename test."
    source.write_text(content, encoding="utf-8")
    return str(source), content

def test_file_rename_success(tmp_path, sample_file):
    source_path, content = sample_file
    destination_path = str(tmp_path / "renamed.txt")
    tool = FileRenameTool()
    result = tool._run(source_path, destination_path)
    assert "Successfully renamed file" in result
    # Check that source file no longer exists and destination file exists with correct content.
    assert not os.path.exists(source_path)
    assert os.path.isfile(destination_path)
    renamed_content = Path(destination_path).read_text(encoding="utf-8")
    assert renamed_content == content

def test_file_rename_source_not_exist(tmp_path):
    source_path = str(tmp_path / "nonexistent.txt")
    destination_path = str(tmp_path / "renamed.txt")
    tool = FileRenameTool()
    result = tool._run(source_path, destination_path)
    assert "Error: Source file" in result

def test_file_rename_no_overwrite(tmp_path, sample_file):
    source_path, content = sample_file
    destination_path = str(tmp_path / "renamed.txt")
    tool = FileRenameTool()
    # Create destination file first.
    with open(destination_path, "w", encoding="utf-8") as f:
        f.write("Existing content")
    result = tool._run(source_path, destination_path, overwrite=False)
    assert "Error: Destination file" in result
    # Ensure both source file and destination file remain unchanged.
    assert os.path.isfile(source_path)
    existing_content = Path(destination_path).read_text(encoding="utf-8")
    assert existing_content == "Existing content"

def test_file_rename_overwrite(tmp_path, sample_file):
    source_path, content = sample_file
    destination_path = str(tmp_path / "renamed.txt")
    tool = FileRenameTool()
    # Create destination file first.
    with open(destination_path, "w", encoding="utf-8") as f:
        f.write("Existing content")
    result = tool._run(source_path, destination_path, overwrite=True)
    assert "Successfully renamed file" in result
    # Check that source file no longer exists and destination file has the content from source file.
    assert not os.path.exists(source_path)
    renamed_content = Path(destination_path).read_text(encoding="utf-8")
    assert renamed_content == content 