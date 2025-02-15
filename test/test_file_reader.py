import pytest
from pathlib import Path
from agent_coding_template.tools.file_reader import FileReaderTool

# Fixture that creates a temporary file with known content.
@pytest.fixture
def sample_file(tmp_path: Path):
    content = "This is a sample file content for testing FileReaderTool."
    file_path = tmp_path / "sample.txt"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path), content

def test_read_file(sample_file):
    """Test reading the entire file content."""
    file_path, expected_content = sample_file
    tool = FileReaderTool()
    result = tool._run(file_path)
    assert result == expected_content

def test_read_file_with_max_chars(sample_file):
    """Test reading the file with a maximum character limit."""
    file_path, expected_content = sample_file
    max_chars = 10
    tool = FileReaderTool()
    result = tool._run(file_path, max_chars=max_chars)
    assert result == expected_content[:max_chars]

def test_invalid_file_path(tmp_path: Path):
    """Test that an invalid file path returns an appropriate error message."""
    invalid_path = str(tmp_path / "non_existent.txt")
    tool = FileReaderTool()
    result = tool._run(invalid_path)
    assert "Error: The provided path" in result

@pytest.mark.asyncio
async def test_arun_read_file(sample_file):
    """Test asynchronous reading of a file."""
    file_path, expected_content = sample_file
    tool = FileReaderTool()
    result = await tool._arun(file_path)
    assert result == expected_content

@pytest.mark.asyncio
async def test_arun_read_file_with_max_chars(sample_file):
    """Test asynchronous reading of a file with a max_chars limit."""
    file_path, expected_content = sample_file
    max_chars = 15
    tool = FileReaderTool()
    result = await tool._arun(file_path, max_chars=max_chars)
    assert result == expected_content[:max_chars]
