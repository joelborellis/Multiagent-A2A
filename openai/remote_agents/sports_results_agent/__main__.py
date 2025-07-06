import logging

import click
import httpx

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, InMemoryPushNotifier
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import OpenAIWebSearchAgentExecutor
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


@click.command()
@click.option('--host', default='localhost')
@click.option('--port', default=10001)
def main(host, port):
    """Starts the OpenAI Agents server using A2A."""
    httpx_client = httpx.AsyncClient()
    request_handler = DefaultRequestHandler(
        agent_executor=OpenAIWebSearchAgentExecutor(),
        task_store=InMemoryTaskStore(),
        push_notifier=InMemoryPushNotifier(httpx_client),
    )

    server = A2AStarletteApplication(
        agent_card=get_agent_card(host, port), http_handler=request_handler
    )
    import uvicorn

    uvicorn.run(server.build(), host=host, port=port)


def get_agent_card(host: str, port: int):
    """Returns the Agent Card for the Semantic Kernel MCP Agent."""

    # Build the agent card
    capabilities = AgentCapabilities(streaming=True)
    skill_mcp_tools = AgentSkill(
        id='sports_results_agent',
        name='Sports Results Agent',
        description=(
            'Provides sports results from various sports leagues.  Include scores, who won, and other relevant information.'
        ),
        tags=['mlb', 'nba', 'nascar', 'golf','colege football'],
        examples=[
            'Show score for Pirates game last night',
            'What was the final score of the game 7 NBA finals and who won?',
            'Whow won the 2025 US Golf Open Championship and where was it played?',
        ],
    )

    agent_card = AgentCard(
        name='SportsResultsAgent',
        description=(
            'This agent provides sports results for various sports leagues such as MLB, NBA, NASCAR, and Golf. '
        ),
        url=f'http://localhost:10001/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=capabilities,
        skills=[skill_mcp_tools],
    )

    return agent_card


if __name__ == '__main__':
    main()