import pytest
from agent_coding_template.tools.readme_reader import ReadmeReaderTool

def test_valid_readme(tmp_path):
    """
    Test that ReadmeReaderTool correctly reads the contents of a README.md file.
    """
    readme_content = "This is the README for the project."
    # Create a temporary README.md file
    (tmp_path / "README.md").write_text(readme_content, encoding="utf-8")
    tool = ReadmeReaderTool()
    result = tool._run(str(tmp_path))
    assert result == readme_content

def test_missing_readme(tmp_path):
    """
    Test that ReadmeReaderTool returns an error message when README.md is missing.
    """
    tool = ReadmeReaderTool()
    result = tool._run(str(tmp_path))
    assert "Error: README.md not found" in result

def test_invalid_directory():
    """
    Test that an invalid directory input returns an appropriate error message.
    """
    tool = ReadmeReaderTool()
    invalid_dir = "/non_existent_directory_path"
    result = tool._run(invalid_dir)
    assert "Error: The provided path" in result

def test_max_chars(tmp_path):
    """
    Test that the tool correctly truncates the output based on max_chars parameter.
    """
    readme_content = "This is a long README file content used for testing."
    (tmp_path / "README.md").write_text(readme_content, encoding="utf-8")
    tool = ReadmeReaderTool()
    max_chars = 10
    result = tool._run(str(tmp_path), max_chars=max_chars)
    assert result == readme_content[:max_chars]

@pytest.mark.asyncio
async def test_arun(tmp_path):
    """
    Test the asynchronous _arun method of the ReadmeReaderTool.
    """
    readme_content = "Async version of README content."
    (tmp_path / "README.md").write_text(readme_content, encoding="utf-8")
    tool = ReadmeReaderTool()
    result = await tool._arun(str(tmp_path))
    assert result == readme_content 