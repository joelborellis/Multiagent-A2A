"""Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import asyncio
import traceback  # Import the traceback module

from collections.abc import AsyncIterator
from pprint import pformat

import gradio as gr

from routing_agent import (
    root_agent as routing_agent,
)
from agents import Runner

#ROUTING_AGENT_RUNNER = Runner()

async def get_response_from_agent(
    message: str,
    history: list[gr.ChatMessage],
) -> AsyncIterator[gr.ChatMessage]:
    """Get response from host agent."""
    try:
        # Use OpenAI Agent Runner's run_streamed method
        print(f"Input message: {message}")
        
        # Get the streaming result object
        stream_result = Runner.run_streamed(routing_agent, message)
        print(f"Stream result type: {type(stream_result)}")
        print(f"Stream result dir: {dir(stream_result)}")
        
        accumulated_text = ""
        
        print("Starting stream iteration...")
        
        # Use the proper streaming approach based on the agents library pattern
        try:
            print("Using stream_events() method...")
            async for event in stream_result.stream_events():
                print(f"Received event: {type(event)} - Type: {getattr(event, 'type', 'no type')}")
                if event.type == "run_item_stream_event":
                    print(f"Got event of type {event.item.__class__.__name__}")
                
                # Handle raw response events that contain actual text deltas
                if (hasattr(event, 'type') and event.type == 'raw_response_event' and 
                    hasattr(event, 'data')):
                    
                    data = event.data
                    data_type = type(data).__name__
                    print(f"Raw response event data type: {data_type}")
                    
                    # Extract text delta from ResponseTextDeltaEvent
                    if data_type == 'ResponseTextDeltaEvent' and hasattr(data, 'delta'):
                        delta_text = data.delta
                        if delta_text:  # Only yield if there's actual content
                            accumulated_text += delta_text
                            yield gr.ChatMessage(
                                role='assistant', 
                                content=accumulated_text
                            )
                    # Handle other response events that might contain content
                    elif hasattr(data, 'content') and isinstance(data.content, str):
                        accumulated_text += data.content
                        yield gr.ChatMessage(
                            role='assistant', 
                            content=accumulated_text
                        )
                
                # Handle agent update events (these are informational)
                elif (hasattr(event, 'type') and 
                      event.type in ['agent_updated_stream_event']):
                    print(f"Agent updated event received (informational only)")
                    # These events don't contain user-facing content, just continue
                    continue
                
                # Handle other event types that might contain direct content
                elif hasattr(event, 'content') and isinstance(event.content, str):
                    accumulated_text += event.content
                    yield gr.ChatMessage(
                        role='assistant', 
                        content=accumulated_text
                    )
                elif isinstance(event, str):
                    accumulated_text += event
                    yield gr.ChatMessage(
                        role='assistant', 
                        content=accumulated_text
                    )
                else:
                    # Log unknown event types for debugging
                    print(f"Unhandled event type: {type(event)}")
                    if hasattr(event, 'type'):
                        print(f"Event type: {event.type}")
                    if hasattr(event, '__dict__'):
                        print(f"Event attributes: {list(event.__dict__.keys())}")
        
        except Exception as stream_error:
            print(f"Stream processing failed: {stream_error}")
            traceback.print_exc()
            
            # Fallback: Try to get final result
            try:
                if hasattr(stream_result, 'result'):
                    print("Trying to get final result...")
                    final_result = await stream_result.result()
                    if final_result:
                        yield gr.ChatMessage(
                            role='assistant',
                            content=str(final_result)
                        )
                else:
                    print("No result method found, treating stream_result as final result")
                    yield gr.ChatMessage(
                        role='assistant',
                        content=str(stream_result)
                    )
            except Exception as fallback_error:
                print(f"Fallback also failed: {fallback_error}")
                traceback.print_exc()
        
        print(f"Stream completed. Final text: {accumulated_text}")
        
        # If no content was streamed, try to get the final result
        if not accumulated_text:
            print("No content streamed, checking for final result...")
            yield gr.ChatMessage(
                role='assistant',
                content='No response received from the agent.'
            )
    except Exception as e:
        print(f'Error in get_response_from_agent (Type: {type(e)}): {e}')
        traceback.print_exc()  # This will print the full traceback
        yield gr.ChatMessage(
            role='assistant',
            content='An error occurred while processing your request. Please check the server logs for details.',
        )


async def main():
    """Main gradio app."""
    with gr.Blocks(
        theme=gr.themes.Ocean(), title='A2A Host Agent with Logo'
    ) as demo:
        gr.Image(
            'static/a2a.png',
            width=100,
            height=100,
            scale=0,
            show_label=False,
            show_download_button=False,
            container=False,
            show_fullscreen_button=False,
        )
        gr.ChatInterface(
            get_response_from_agent,
            title='A2A Host Agent',  # Title can be handled by Markdown above
            description='This assistant can help you to get sports news and sports results',
        )

    print('Launching Gradio interface...')
    demo.queue().launch(
        server_name='0.0.0.0',
        server_port=8084,
    )
    print('Gradio application has been shut down.')


if __name__ == '__main__':
    asyncio.run(main())