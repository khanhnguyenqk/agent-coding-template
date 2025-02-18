"""
Utility to pretty print agent/tool message chunks.
"""

def get_field(obj, field, default=None):
    """
    Helper to get a value from either a dict or an attribute of an object.
    """
    if isinstance(obj, dict):
        return obj.get(field, default)
    return getattr(obj, field, default)

def pretty_print_chunk(chunk: dict, max_content_length: int = 200) -> None:
    """
    Pretty prints a chunk object containing agent messages or tool responses.

    If the chunk contains an "agent" key, it prints each message's content,
    including text and tool call details as well as metadata if available.

    If the chunk contains a "tools" key, it prints each tool response with
    its name, ID, truncated content (if longer than max_content_length), and tool call ID.

    For any unknown chunk structure, it prints the raw chunk.

    Args:
        chunk (dict): The message chunk to pretty print.
        max_content_length (int, optional): Maximum number of characters to show for tool response content.
            Defaults to 200.
    """
    if "agent" in chunk:
        print("\n=== AGENT MESSAGE ===")
        print(chunk)
        messages = get_field(chunk["agent"], "messages", [])
        if not isinstance(messages, list):
            messages = [messages]
        for message in messages:
            # Obtain the content from the message and handle different types.
            content_field = get_field(message, "content", [])
            if isinstance(content_field, str):
                # Content is a string so print it directly as text.
                print("\nText:", content_field)
            elif isinstance(content_field, list):
                for content in content_field:
                    ctype = get_field(content, "type", None)
                    if ctype == "text":
                        text = get_field(content, "text", "")
                        print("\nText:", text)
                    elif ctype == "tool_use":
                        print("\nTool Call:")
                        print("  Tool:", get_field(content, "name", "N/A"))
                        print("  ID:", get_field(content, "id", "N/A"))
                        print("  Parameters:")
                        inputs = get_field(content, "input", {})
                        for key, val in inputs.items():
                            print(f"    {key}: {val}")
                    else:
                        print("\nOther Content:", content)
            else:
                # For any other type, print the content directly.
                print("\nOther Content:", content_field)
            # Optionally print metadata if available
            metadata = get_field(message, "response_metadata", None)
            if metadata:
                print("\nMetadata:")
                stop_reason = metadata.get("stop_reason") if isinstance(metadata, dict) else get_field(metadata, "stop_reason", "N/A")
                usage = metadata.get("usage") if isinstance(metadata, dict) else get_field(metadata, "usage", "N/A")
                print("  Stop reason:", stop_reason)
                print("  Tokens:", usage)
            print("\n" + "=" * 100 + "\n")

    elif "tools" in chunk:
        print("\n=== TOOL RESPONSE ===")
        print(chunk)
        messages = get_field(chunk["tools"], "messages", [])
        if not isinstance(messages, list):
            messages = [messages]
        for message in messages:
            print("\nTool:", get_field(message, "name", "Unknown Tool"))
            print("ID:", get_field(message, "id", "Unknown ID"))
            content = get_field(message, "content", "")
            if isinstance(content, str) and len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            print("Content:", content)
            print("Tool Call ID:", get_field(message, "tool_call_id", "N/A"))
            print("\n" + "=" * 100 + "\n")
    else:
        print("Unknown chunk format:")
        print(chunk)
