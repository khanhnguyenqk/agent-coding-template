from agent_coding_template.tools.directory_mapper import DirectoryMapperTool
import os
import json
import pytest

def test_directory_mapper_valid(tmp_path):
    """
    Test DirectoryMapperTool with a valid temporary directory structure.
    """
    # Create a temporary directory structure.
    base_dir = tmp_path  # tmp_path is a pathlib.Path object provided by pytest
    # Create a file in the root of the temporary directory.
    (base_dir / "root_file.txt").write_text("Root file content")
    # Create a subdirectory and a file within it.
    subdir = base_dir / "subdir"
    subdir.mkdir()
    (subdir / "sub_file.txt").write_text("Sub file content")
    
    tool = DirectoryMapperTool()
    output = tool._run(str(base_dir))

    print(output)
    
    # Verify that the output contains the expected directory and file names.
    assert "root_file.txt" in output
    assert "subdir/" in output
    assert "sub_file.txt" in output

def test_directory_mapper_invalid():
    """
    Test DirectoryMapperTool with an invalid directory path.
    """
    tool = DirectoryMapperTool()
    output = tool._run("non_existent_directory")
    assert "Error:" in output

def test_directory_mapper_json_valid(tmp_path):
    """
    Test DirectoryMapperTool with JSON output format.
    """
    # Create a temporary directory structure.
    # Create a file in the root of the temporary directory.
    (tmp_path / "a.txt").write_text("Content A")
    # Create a subdirectory and a file within it.
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "b.txt").write_text("Content B")
    
    tool = DirectoryMapperTool()
    output = tool._run(str(tmp_path), output_format="json")
    parsed = json.loads(output)

    print(output)
    
    # Verify that the root node is a directory with a children key.
    assert parsed["type"] == "directory"
    assert "children" in parsed
    
    # Check that both 'a.txt' and 'subdir' appear among the children.
    child_names = sorted(child["name"] for child in parsed["children"])
    assert child_names == ["a.txt", "subdir"]

@pytest.mark.asyncio
async def test_directory_mapper_arun(tmp_path):
    """
    Test the asynchronous _arun method of DirectoryMapperTool.
    """
    # Create a temporary directory structure with a file.
    (tmp_path / "test_file.txt").write_text("Some test content")
    
    tool = DirectoryMapperTool()
    output = await tool._arun(str(tmp_path), output_format="ascii")
    
    # Verify that the asynchronous method returns the same expected ascii output.
    assert "test_file.txt" in output

def test_directory_mapper_empty_directory(tmp_path):
    """
    Test DirectoryMapperTool with an empty directory.
    """
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    
    tool = DirectoryMapperTool()
    output = tool._run(str(empty_dir))
    
    # Expecting only the directory name with a trailing '/'.
    expected = f"{empty_dir.name}/"
    # The output should be exactly one line.
    assert output.strip() == expected

def test_directory_mapper_permission(monkeypatch, tmp_path):
    """
    Test DirectoryMapperTool when a PermissionError is raised during directory listing.
    """
    base_dir = tmp_path / "test_dir"
    base_dir.mkdir()
    protected = base_dir / "protected"
    protected.mkdir()
    # Create a file inside the protected directory.
    (protected / "secret.txt").write_text("top secret")
    
    original_listdir = os.listdir  # Save original os.listdir

    def fake_listdir(path):
        # Simulate a PermissionError only for the 'protected' directory.
        if os.path.basename(path) == "protected":
            raise PermissionError("Permission Denied")
        return original_listdir(path)

    monkeypatch.setattr(os, "listdir", fake_listdir)
    
    tool = DirectoryMapperTool()
    output = tool._run(str(base_dir))
    
    # Verify that the output for the protected directory indicates a permission error.
    assert "[Permission Denied]" in output

def test_directory_mapper_hidden_files(tmp_path):
    """
    Test that hidden files (those starting with '.') are included only when show_hidden is True.
    """
    # Create a temporary directory
    test_dir = tmp_path / "hidden_test"
    test_dir.mkdir()

    # Create a visible file and a hidden file.
    visible_file = test_dir / "visible.txt"
    visible_file.write_text("visible content")

    hidden_file = test_dir / ".hidden.txt"
    hidden_file.write_text("hidden content")

    tool = DirectoryMapperTool()

    # Test ASCII output without hidden files
    ascii_without_hidden = tool._run(str(test_dir), output_format="ascii", show_hidden=False)
    assert "visible.txt" in ascii_without_hidden
    assert ".hidden.txt" not in ascii_without_hidden

    # Test ASCII output including hidden files
    ascii_with_hidden = tool._run(str(test_dir), output_format="ascii", show_hidden=True)
    assert "visible.txt" in ascii_with_hidden
    assert ".hidden.txt" in ascii_with_hidden

    # Test JSON output without hidden files
    json_without_hidden = json.loads(tool._run(str(test_dir), output_format="json", show_hidden=False))
    children_names = [child["name"] for child in json_without_hidden.get("children", [])]
    assert "visible.txt" in children_names
    assert ".hidden.txt" not in children_names

    # Test JSON output including hidden files
    json_with_hidden = json.loads(tool._run(str(test_dir), output_format="json", show_hidden=True))
    children_names = [child["name"] for child in json_with_hidden.get("children", [])]
    assert "visible.txt" in children_names
    assert ".hidden.txt" in children_names
