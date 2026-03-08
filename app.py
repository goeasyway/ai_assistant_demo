import os
import chainlit as cl
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import StreamEvent

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

SYSTEM_PROMPT = f"""You are a helpful office assistant. Follow these rules strictly:
1. Keep answers concise and to the point.
2. The current system is macOS. Use python3 and pip3 for all Python-related commands.
3. You can help users create and process office documents (Excel, Word, PDF) using Python libraries (e.g. openpyxl, python-docx, reportlab, pandas) or macOS built-in capabilities. Install missing libraries with pip3 when necessary.
4. For Excel data processing, prefer using pandas.
5. Before installing any Python library, first check if it is already installed (e.g. pip3 show <package>). Only install if not present.
6. You may ONLY read and write files within the project directory and its subdirectories. Project directory: {PROJECT_DIR}
"""


@cl.on_chat_start
async def start():
    cl.user_session.set("session_id", None)


@cl.on_message
async def main(user_message: cl.Message):
    # Your custom logic goes here...
    msg = cl.Message(content="")
    await msg.send()

    # Track tool call state
    current_step = None
    tool_input = ""
    in_tool = False

    # Build prompt with attachments info
    prompt = user_message.content
    if user_message.elements:
        attachments_info = "\n\nAttached files:\n"
        for element in user_message.elements:
            attachments_info += f"- Filename: {element.name}, Path: {element.path}\n"
        prompt += attachments_info

    # Build options with session continuity
    session_id = cl.user_session.get("session_id")
    options = ClaudeAgentOptions(
        include_partial_messages=True,
        system_prompt=SYSTEM_PROMPT,
        allowed_tools=["Bash", "Glob", "Read", "Write", "Edit", "Grep", "WebSearch", "WebFetch"],
    )
    if session_id:
        options.resume = session_id
        options.continue_conversation = True

    async for message in query(
        prompt=prompt,
        options=options,
    ):
        # Capture session_id from the first StreamEvent
        if isinstance(message, StreamEvent) and not cl.user_session.get("session_id"):
            cl.user_session.set("session_id", message.session_id)

        if isinstance(message, StreamEvent):
            event = message.event
            event_type = event.get("type")

            if event_type == "content_block_start":
                content_block = event.get("content_block", {})
                if content_block.get("type") == "tool_use":
                    # Tool call starting - create a Step in Chainlit
                    tool_name = content_block.get("name", "tool")
                    current_step = cl.Step(name=tool_name, type="tool")
                    current_step.input = ""
                    tool_input = ""
                    in_tool = True
                    await current_step.send()
                elif content_block.get("type") == "thinking":
                    # Thinking block starting
                    current_step = cl.Step(name="Thinking", type="llm")
                    current_step.output = ""
                    in_tool = True
                    await current_step.send()

            elif event_type == "content_block_delta":
                delta = event.get("delta", {})
                delta_type = delta.get("type")

                if delta_type == "text_delta" and not in_tool:
                    # Stream text to main message
                    token = delta.get("text", "")
                    if token:
                        await msg.stream_token(token)

                elif delta_type == "input_json_delta" and current_step:
                    # Accumulate tool input
                    chunk = delta.get("partial_json", "")
                    tool_input += chunk
                    current_step.input = tool_input
                    await current_step.update()

                elif delta_type == "thinking_delta" and current_step:
                    # Stream thinking content to step
                    chunk = delta.get("thinking", "")
                    current_step.output += chunk
                    await current_step.update()

            elif event_type == "content_block_stop":
                if in_tool and current_step:
                    # Finalize the step
                    await current_step.update()
                    current_step = None
                    in_tool = False
                    tool_input = ""

    await msg.update()
