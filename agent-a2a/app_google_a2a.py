import os
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent_executor import (
    HelloWorldAgentExecutor,  # type: ignore[import-untyped]
)

skill = AgentSkill(
    id='hello_world',
    name='Returns hello world',
    description='just returns hello world',
    tags=['hello world'],
    examples=['hi', 'hello world'],
)

extended_skill = AgentSkill(
    id='super_hello_world',
    name='Returns a SUPER Hello World',
    description='A more enthusiastic greeting, only for authenticated users.',
    tags=['hello world', 'super', 'extended'],
    examples=['super hi', 'give me a super hello'],
)

def get_code_engine_urls():
    public_url, private_url = None, None
    try:
        # These env variables are automatically injected by Code Engine
        app_name = os.environ['CE_APP']  # Get the application name.
        subdomain = os.environ['CE_SUBDOMAIN']  # Get the subdomain.
        domain = os.environ['CE_DOMAIN']  # Get the domain name.

        public_url = f"https://{app_name}.{subdomain}.{domain}/"
        private_url = f"https://{app_name}.{subdomain}.private.{domain}/" # Construct the private URL.
    except KeyError as e:
        print(f"Error: Required environment variable {e} not found.")
        print("Application may be running locally otherwise required env vars are missing.\n")
    return public_url, private_url


public_url, _ = get_code_engine_urls()
if not public_url:
    public_url = "http://localhost:8000/"  # Fallback for local development
url=public_url,
public_agent_card = AgentCard(
    name='A2A Hello World Agent on IBM Servless',
    description='Just a hello world agent',
    url=public_url,
    version='1.0.0',
    default_input_modes=['text'],
    default_output_modes=['text'],
    capabilities=AgentCapabilities(streaming=True),
    skills=[skill],  # Only the basic skill for the public card
    supports_authenticated_extended_card=True,
)

specific_extended_agent_card = public_agent_card.model_copy(
    update={
        'name': 'Hello World Agent - Extended Edition',  # Different name for clarity
        'description': 'The full-featured hello world agent for authenticated users.',
        'version': '1.0.1',  # Could even be a different version
        # Capabilities and other fields like url, default_input_modes, default_output_modes,
        # supports_authenticated_extended_card are inherited from public_agent_card unless specified here.
        'skills': [
            skill,
            extended_skill,
        ],  # Both skills for the extended card
    }
)

request_handler = DefaultRequestHandler(
    agent_executor=HelloWorldAgentExecutor(),
    task_store=InMemoryTaskStore(),
)

server = A2AStarletteApplication(
    agent_card=public_agent_card,
    http_handler=request_handler,
    extended_agent_card=specific_extended_agent_card,
)

app = server.build()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
