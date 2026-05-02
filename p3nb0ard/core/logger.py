import logging
from rich.console import Console
from rich.logging import RichHandler

# A rich console instance for printing custom UI elements
console = Console()

def setup_logger():
    """
    Sets up a custom logger that writes to both the console (using Rich)
    and a local file (agent_run.log).
    """
    logger = logging.getLogger("PentestAgent")
    logger.setLevel(logging.DEBUG)

    # File handler for complete history
    file_handler = logging.FileHandler("agent_run.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Rich console handler for beautiful terminal output
    rich_handler = RichHandler(console=console, markup=True)
    rich_handler.setLevel(logging.INFO)
    rich_formatter = logging.Formatter('%(message)s')
    rich_handler.setFormatter(rich_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(rich_handler)

    return logger

agent_logger = setup_logger()
