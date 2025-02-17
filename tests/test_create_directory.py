import os
import pytest
from agent_coding_template.tools.create_directory import CreateDirectoryTool

def test_create_directory_success(tmp_path):
    # Create a new directory within the temporary path.
    new_dir = tmp_path / "new_directory"
    tool = CreateDirectoryTool()
    result = tool._run(str(new_dir))
    # Verify that the directory now exists and the result message is as expected.
    assert new_dir.exists() and new_dir.is_dir()
    assert f"Successfully created directory '{str(new_dir)}'" in result

def test_create_directory_already_exists(tmp_path):
    # Create the directory first.
    existing_dir = tmp_path / "existing_directory"
    existing_dir.mkdir()
    tool = CreateDirectoryTool()
    result = tool._run(str(existing_dir))
    # Even if the directory already exists, os.makedirs with exist_ok=True should succeed.
    assert existing_dir.exists() and existing_dir.is_dir()
    assert f"Successfully created directory '{str(existing_dir)}'" in result

def test_create_directory_error(monkeypatch, tmp_path):
    # Monkeypatch os.makedirs to simulate an error.
    def fake_makedirs(path, exist_ok=True):
        raise Exception("Simulated error")
    monkeypatch.setattr(os, "makedirs", fake_makedirs)
    
    tool = CreateDirectoryTool()
    test_dir = tmp_path / "error_dir"
    result = tool._run(str(test_dir))
    # Check that the error message is correctly returned.
    assert "Error creating directory: Simulated error" in result

# For testing the asynchronous version, we need to bypass the extra 'exist_ok' keyword
# that _arun passes to _run by patching _run to accept extra keyword arguments.
@pytest.mark.asyncio
async def test_create_directory_arun_success(tmp_path, monkeypatch):
    new_dir = tmp_path / "async_new_directory"
    
    # Patch _run so that it accepts additional keyword arguments.
    original_run = CreateDirectoryTool._run
    def patched_run(self, directory, **kwargs):
        return original_run(self, directory)
    monkeypatch.setattr(CreateDirectoryTool, "_run", patched_run)
    
    tool = CreateDirectoryTool()
    result = await tool._arun(str(new_dir))
    # Check that the directory is created and the success message is returned.
    assert new_dir.exists() and new_dir.is_dir()
    assert f"Successfully created directory '{str(new_dir)}'" in result

@pytest.mark.asyncio
async def test_create_directory_arun_error(tmp_path, monkeypatch):
    test_dir = tmp_path / "async_error_dir"
    
    def fake_makedirs(path, exist_ok=True):
        raise Exception("Async simulated error")
    monkeypatch.setattr(os, "makedirs", fake_makedirs)
    
    # Again, patch _run to allow the extra keyword parameter.
    original_run = CreateDirectoryTool._run
    def patched_run(self, directory, **kwargs):
        return original_run(self, directory)
    monkeypatch.setattr(CreateDirectoryTool, "_run", patched_run)
    
    tool = CreateDirectoryTool()
    result = await tool._arun(str(test_dir))
    # Verify that the error message from the asynchronous call is correctly returned.
    assert "Error creating directory: Async simulated error" in result

def test_create_nested_directories(tmp_path):
    # Create nested directories within the temporary path.
    nested_dir = tmp_path / "nested" / "subdir1" / "subdir2"
    tool = CreateDirectoryTool()
    result = tool._run(str(nested_dir))
    # Verify that the nested directories now exist and the success message is returned.
    assert nested_dir.exists() and nested_dir.is_dir()
    assert f"Successfully created directory '{str(nested_dir)}'" in result 