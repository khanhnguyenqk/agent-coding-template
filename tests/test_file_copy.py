import os
import pytest
from pathlib import Path
from agent_coding_template.tools.file_copy import FileCopyTool

@pytest.fixture
def sample_file(tmp_path: Path):
    # Create a sample source file
    source = tmp_path / "source.txt"
    content = "Sample content for file copy test."
    source.write_text(content, encoding="utf-8")
    return str(source), content

def test_file_copy_success(tmp_path, sample_file):
    source_path, content = sample_file
    destination_path = str(tmp_path / "copied.txt")
    tool = FileCopyTool()
    result = tool._run(source_path, destination_path)
    assert "Successfully copied file" in result
    # Verify file exists and content matches
    assert os.path.isfile(destination_path)
    copied_content = Path(destination_path).read_text(encoding="utf-8")
    assert copied_content == content

def test_file_copy_source_not_exist(tmp_path):
    source_path = str(tmp_path / "nonexistent.txt")
    destination_path = str(tmp_path / "copied.txt")
    tool = FileCopyTool()
    result = tool._run(source_path, destination_path)
    assert "Error: Source file" in result

def test_file_copy_no_overwrite(tmp_path, sample_file):
    source_path, content = sample_file
    destination_path = str(tmp_path / "copied.txt")
    # First copy to destination
    tool = FileCopyTool()
    result1 = tool._run(source_path, destination_path)
    assert "Successfully copied file" in result1
    # Modify source file content
    with open(source_path, "w", encoding="utf-8") as f:
        f.write("Modified content")
    # Attempt copy without overwrite
    result2 = tool._run(source_path, destination_path, overwrite=False)
    assert "Error: Destination file" in result2
    # Ensure destination file content remains unchanged from first copy
    copied_content = Path(destination_path).read_text(encoding="utf-8")
    assert copied_content == content

def test_file_copy_overwrite(tmp_path, sample_file):
    source_path, content = sample_file
    destination_path = str(tmp_path / "copied.txt")
    tool = FileCopyTool()
    result1 = tool._run(source_path, destination_path)
    assert "Successfully copied file" in result1
    # Change source content
    new_content = "New file content for overwrite test."
    Path(source_path).write_text(new_content, encoding="utf-8")
    # Copy with overwrite enabled
    result2 = tool._run(source_path, destination_path, overwrite=True)
    assert "Successfully copied file" in result2
    # Check that destination file now has new content
    copied_content = Path(destination_path).read_text(encoding="utf-8")
    assert copied_content == new_content 