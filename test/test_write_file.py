import pytest
from agent_coding_template.tools.write_file import WriteFileTool

def test_write_file_success(tmp_path):
    """
    Test that WriteFileTool writes content to a file successfully.
    """
    file_path = tmp_path / "test_file.py"
    content = "print('Hello, world!')"
    tool = WriteFileTool()
    result = tool._run(str(file_path), content, overwrite=True)
    assert "Successfully wrote to file" in result
    # Verify that the file contains the correct content.
    written = file_path.read_text(encoding="utf-8")
    assert written == content

def test_no_overwrite(tmp_path):
    """
    Test that WriteFileTool does not overwrite an existing file when overwrite is set to False.
    """
    file_path = tmp_path / "test_file.md"
    original_content = "Original content"
    file_path.write_text(original_content, encoding="utf-8")
    tool = WriteFileTool()
    new_content = "New content that should not overwrite."
    result = tool._run(str(file_path), new_content, overwrite=False)
    assert "Error: File" in result
    # The file should retain its original content.
    written = file_path.read_text(encoding="utf-8")
    assert written == original_content

def test_create_directory(tmp_path):
    """
    Test that WriteFileTool creates missing directories and writes the file.
    """
    subdir = tmp_path / "subdir1" / "subdir2"
    file_path = subdir / "config.json"
    content = '{"key": "value"}'
    tool = WriteFileTool()
    result = tool._run(str(file_path), content, overwrite=True)
    assert "Successfully wrote to file" in result
    # Verify that the file exists and contains the expected content.
    assert file_path.exists()
    written = file_path.read_text(encoding="utf-8")
    assert written == content

@pytest.mark.asyncio
async def test_arun_write_file(tmp_path):
    """
    Test the asynchronous _arun method of WriteFileTool.
    """
    file_path = tmp_path / "async_test.txt"
    content = "Async file write test."
    tool = WriteFileTool()
    result = await tool._arun(str(file_path), content, overwrite=True)
    assert "Successfully wrote to file" in result
    written = file_path.read_text(encoding="utf-8")
    assert written == content 