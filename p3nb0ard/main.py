import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from core.llm_client import OllamaClient
from core.agent import Agent
from core.logger import agent_logger
from cli import start_cli


def main():
    stream = "--stream" in sys.argv
    if stream:
        agent_logger.info("Starting P3NB0ARD in STREAMING mode...")
    else:
        agent_logger.info("Starting P3NB0ARD...")

    # Initialize the direct Ollama client (no frameworks)
    client = OllamaClient(stream=stream)

    # Create the autonomous agent
    agent = Agent(client)

    # Start the interactive CLI
    start_cli(agent)


if __name__ == "__main__":
    main()
