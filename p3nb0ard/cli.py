import os
import subprocess
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()


def run_local_shell(command: str):
    """Executes a command directly on the host bypassing the agent."""
    try:
        cmd_to_run = command[1:].strip()
        if not cmd_to_run:
            return

        console.print(f"[bold cyan]Running local command:[/bold cyan] {cmd_to_run}")
        subprocess.run(cmd_to_run, shell=True)
    except Exception as e:
        console.print(f"[bold red]Error running command: {e}[/bold red]")


def start_cli(agent):
    """
    Starts the interactive CLI loop.
    """
    console.print(Panel(
        "[bold green]P3NB0ARD Autonomous Hacker Agent Initialized.[/bold green]\n"
        "[dim]- Type normally to interact with the autonomous agent.\n"
        "- Prefix with ! to execute local commands (e.g., !ls, !nmap 10.10.10.5).\n"
        "- Type !clear to clear the screen.\n"
        "- Type !exit to quit.[/dim]",
        title="[bold red]Terminal Overdrive[/bold red]",
        border_style="red"
    ))

    while True:
        try:
            user_input = Prompt.ask("\n[bold red]p3nb0ard[/bold red] [bold yellow]>[/bold yellow]")

            if not user_input.strip():
                continue

            if user_input.lower() == "!exit":
                console.print("[bold red]Shutting down...[/bold red]")
                break
            elif user_input.lower() == "!clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            elif user_input.startswith("!"):
                run_local_shell(user_input)
                continue

            # Pass to the autonomous agent
            console.print("[dim italic]Agent engaged — autonomous mode active...[/dim italic]")
            try:
                result = agent.run(user_input)
                console.print(Panel(
                    str(result),
                    title="[bold green]🎯 Final Report[/bold green]",
                    border_style="green"
                ))
            except KeyboardInterrupt:
                console.print("\n[bold yellow]Agent interrupted by user.[/bold yellow]")
            except Exception as e:
                console.print(f"[bold red]Agent error: {e}[/bold red]")

        except KeyboardInterrupt:
            console.print("\n[bold red]Interrupted. Type !exit to quit.[/bold red]")
        except EOFError:
            break
