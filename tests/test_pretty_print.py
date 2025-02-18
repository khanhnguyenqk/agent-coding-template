import io
import sys
from agent_coding_template.utils.pretty_print import pretty_print_chunk

def test_agent_message_output():
    # Test a chunk with agent messages containing text and tool calls.
    agent_chunk = {
        "agent": {
            "messages": [
                {
                    "content": [
                        {"type": "text", "text": "Hello Agent"},
                        {"type": "tool_use", "name": "FileReaderTool", "id": "123", "input": {"file_path": "/dummy/path"}}
                    ],
                    "response_metadata": {"stop_reason": "end", "usage": {"input_tokens": 100}}
                }
            ]
        }
    }
    captured_output = io.StringIO()
    sys.stdout = captured_output
    pretty_print_chunk(agent_chunk)
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    assert "Hello Agent" in output
    assert "FileReaderTool" in output
    assert "file_path" in output
    assert "Stop reason:" in output

def test_tool_response_truncation_default():
    # Test that tool content longer than 200 characters is truncated when using the default value.
    long_content = "a" * 300  # length 300
    tools_chunk = {
        "tools": {
            "messages": [
                {
                    "name": "TestTool",
                    "id": "456",
                    "content": long_content,
                    "tool_call_id": "789"
                }
            ]
        }
    }
    captured_output = io.StringIO()
    sys.stdout = captured_output
    pretty_print_chunk(tools_chunk)  # default max_content_length = 200
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    expected_truncated = "a" * 200 + "..."
    assert expected_truncated in output

def test_tool_response_custom_truncation():
    # Test that specifying a custom max_content_length works.
    long_content = "b" * 50  # length 50, under our custom threshold
    tools_chunk = {
        "tools": {
            "messages": [
                {
                    "name": "CustomTool",
                    "id": "001",
                    "content": long_content,
                    "tool_call_id": "002"
                }
            ]
        }
    }
    captured_output = io.StringIO()
    sys.stdout = captured_output
    pretty_print_chunk(tools_chunk, max_content_length=100)  # custom threshold higher than content length
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    assert long_content in output

def test_unknown_chunk_format():
    # Test that chunks with no recognized keys print the unknown format output.
    unknown_chunk = {"unexpected": "data"}
    captured_output = io.StringIO()
    sys.stdout = captured_output
    pretty_print_chunk(unknown_chunk)
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    assert "Unknown chunk format:" in output

def test_agent_message_output_with_string():
    # Test an agent chunk where the content is directly a string.
    agent_chunk_string = {
        "agent": {
            "messages": [
                {
                    "content": "I've completed all the required actions: tasks are all done."
                }
            ]
        }
    }
    captured_output = io.StringIO()
    sys.stdout = captured_output
    pretty_print_chunk(agent_chunk_string)
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    assert "Text:" in output
    assert "I've completed all the required actions" in output
