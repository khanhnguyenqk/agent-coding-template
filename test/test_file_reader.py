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
    """Test reading the entire file content with line numbers injected (default behavior)."""
    file_path, expected_content = sample_file
    tool = FileReaderTool()
    result = tool._run(file_path)
    # With a single line, the expected output prefix "1: " is added
    assert result == f"1: {expected_content}"

def test_read_file_with_max_chars(sample_file):
    """Test reading the file with a maximum character limit and line numbers injected."""
    file_path, expected_content = sample_file
    max_chars = 10
    tool = FileReaderTool()
    result = tool._run(file_path, max_chars=max_chars)
    expected_truncated = expected_content[:max_chars]
    expected_result = f"1: {expected_truncated}"
    assert result == expected_result

def test_read_file_without_line_numbers(sample_file):
    """Test reading the file with line number injection disabled."""
    file_path, expected_content = sample_file
    tool = FileReaderTool()
    result = tool._run(file_path, inject_line_numbers=False)
    # No injection so output matches the raw file content.
    assert result == expected_content

def test_read_file_multiple_lines(tmp_path):
    """Test reading a file with multiple lines both with and without line numbers."""
    content = "Line one\nLine two\nLine three"
    file_path = tmp_path / "multiline.txt"
    file_path.write_text(content, encoding="utf-8")
    tool = FileReaderTool()
    # Test with default (line number injection enabled)
    result = tool._run(str(file_path))
    expected_injected = "\n".join(f"{i+1}: {line}" for i, line in enumerate(content.splitlines()))
    assert result == expected_injected
    # Test with injection disabled
    result_no_inject = tool._run(str(file_path), inject_line_numbers=False)
    assert result_no_inject == content

@pytest.mark.asyncio
async def test_arun_read_file(sample_file):
    """Test asynchronous reading of a file with default line number injection."""
    file_path, expected_content = sample_file
    tool = FileReaderTool()
    result = await tool._arun(file_path)
    assert result == f"1: {expected_content}"

@pytest.mark.asyncio
async def test_arun_read_file_with_max_chars(sample_file):
    """Test asynchronous reading of a file with max_chars and line number injection."""
    file_path, expected_content = sample_file
    max_chars = 15
    tool = FileReaderTool()
    result = await tool._arun(file_path, max_chars=max_chars)
    expected_result = f"1: {expected_content[:max_chars]}"
    assert result == expected_result

def test_invalid_file_path(tmp_path: Path):
    """Test that an invalid file path returns an appropriate error message."""
    invalid_path = str(tmp_path / "non_existent.txt")
    tool = FileReaderTool()
    result = tool._run(invalid_path)
    assert "Error: The provided path" in result

@pytest.mark.asyncio
async def test_arun_read_file_with_max_chars(sample_file):
    """Test asynchronous reading of a file with a max_chars limit."""
    file_path, expected_content = sample_file
    max_chars = 15
    tool = FileReaderTool()
    result = await tool._arun(file_path, max_chars=max_chars)
    assert result == f"1: {expected_content[:max_chars]}"
