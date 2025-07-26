"""
Multi-agent routing application with Azure AI Agents integration.

This application provides a Gradio interface for interacting with a routing agent
that uses Azure AI Agents for core functionality and delegates tasks to remote agents.
"""

import asyncio
import os
import traceback
from collections.abc import AsyncIterator
from typing import Optional

import gradio as gr

from routing_agent import RoutingAgent

APP_NAME = "azure_routing_app"
USER_ID = "default_user"
SESSION_ID = "default_session"


class RoutingAgentApp:
    """Main application class that manages the routing agent lifecycle."""
    
    def __init__(self):
        self.routing_agent: Optional[RoutingAgent] = None
        self.demo: Optional[gr.Blocks] = None
    
    async def initialize_routing_agent(self):
        """Initialize the Azure AI routing agent."""
        try:
            print("Initializing Azure AI routing agent...")
            
            # Create the routing agent with remote agent addresses
            self.routing_agent = await RoutingAgent.create(
                remote_agent_addresses=[
                    os.getenv('SPORTS_RESULTS_URL', 'http://localhost:10001'),
                    os.getenv('SPORTS_NEWS_URL', 'http://localhost:10002'),
                ]
            )
            
            # Create the Azure AI agent
            azure_agent = self.routing_agent.create_agent()
            print(f"Azure AI routing agent initialized successfully with Name and ID: {azure_agent.name} - {azure_agent.id}")

        except Exception as e:
            print(f"Failed to initialize routing agent: {e}")
            traceback.print_exc()
            raise
    
    async def cleanup_routing_agent(self):
        """Clean up the routing agent resources."""
        if self.routing_agent:
            try:
                self.routing_agent.cleanup()
                print("Routing agent cleaned up successfully.")
            except Exception as e:
                print(f"Error during cleanup: {e}")
            finally:
                self.routing_agent = None
    
    async def get_response_from_agent(
        self,
        message: str,
        history: list[gr.ChatMessage],
    ) -> AsyncIterator[gr.ChatMessage]:
        """Get response from Azure AI Foundry Agent routing by A2A and Semantic Kernel."""
        if not self.routing_agent:
            yield gr.ChatMessage(
                role="assistant",
                content="❌ **Error**: Routing agent not initialized. Please restart the application.",
            )
            return
        
        try:
            # Show that we're processing the request
            yield gr.ChatMessage(
                role="assistant",
                content="🤔 **Processing your request...**",
            )
            
            # Process the message through Azure AI Agent
            response = await self.routing_agent.process_user_message(message)
            
            # Yield the final response
            if response:
                yield gr.ChatMessage(
                    role="assistant", 
                    content=response
                )
            else:
                yield gr.ChatMessage(
                    role="assistant",
                    content="❌ **Error**: No response received from the agent.",
                )
                
        except Exception as e:
            print(f"Error in get_response_from_agent (Type: {type(e)}): {e}")
            traceback.print_exc()
            yield gr.ChatMessage(
                role="assistant",
                content=f"❌ **An error occurred**: {str(e)}\n\nPlease check the server logs for details.",
            )


    
    def create_gradio_interface(self) -> gr.Blocks:
        """Create and configure the Gradio interface."""
        demo = gr.Blocks(theme=gr.themes.Ocean(), title="Azure AI Routing Agent")
        
        with demo:
            # Header section
            gr.Markdown("""
            # 🤖 Azure AI Routing Agent
            
            This assistant uses Azure AI Agents to help you to use playwright and some dev tools.
            The agent intelligently routes your requests to specialized remote agents for optimal assistance.
            """)
            
            # Display agent status
            if self.routing_agent and self.routing_agent.azure_agent:
                gr.Markdown(f"""
                ### 📊 Agent Status
                - **Azure AI Agent ID**: `{self.routing_agent.azure_agent.id}`
                - **Thread ID**: `{self.routing_agent.current_thread.id if self.routing_agent.current_thread else 'Not created'}`
                - **Available Remote Agents**: {len(self.routing_agent.remote_agent_connections)}
                """)
            
            # Chat interface
            gr.ChatInterface(
                self.get_response_from_agent,
                title="💬 Chat with Azure AI Routing Agent",
                description="Give me a message, I will help you to browse the web, clone repo, or open it with VSCode and VSCode Insiders",
                examples=[
                    "Clone repo https://github.com/kinfey/mcpdemo1",
                    "Go to github.com/kinfey",
                    "Open {path} with VSCode or VSCode Insiders",
                ]
            )
            
            # Footer
            gr.Markdown("""
            ---
            **Powered by**: Azure AI Agents | **A2A Framework**: Multi-Agent Routing System with Semantic Kernel and A2A
            """)
        
        return demo
    
    async def run(self):
        """Main application entry point."""
        # Check required environment variables
        required_env_vars = [
            "AZURE_AI_AGENT_ENDPOINT",
            "AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME"
        ]
        
        # Check if application credentials are provided
        app_creds = ["AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID"]
        has_app_creds = all(os.getenv(var) for var in app_creds)
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            print("Please set these environment variables before running the application.")
            return
        
        if has_app_creds:
            print("✅ Using Azure application (service principal) authentication")
        else:
            print("✅ Using DefaultAzureCredential authentication")
            print("   Make sure you're logged in with 'az login' or have other valid credentials")
        
        # Initialize the routing agent
        await self.initialize_routing_agent()

        try:
            # Create and launch the Gradio interface
            self.demo = self.create_gradio_interface()
            
            print("Launching Gradio interface...")
            self.demo.queue().launch(
                server_name="0.0.0.0",
                server_port=8083,
            )
            
        except Exception as e:
            print(f"Error in main application: {e}")
            traceback.print_exc()
        finally:
            print("Shutting down application...")
            await self.cleanup_routing_agent()
            print("Gradio application has been shut down.")


async def main():
    """Main entry point for the application."""
    app = RoutingAgentApp()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())