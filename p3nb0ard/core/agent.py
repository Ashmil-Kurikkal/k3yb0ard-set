import json
from rich.console import Console
from rich.panel import Panel
from core.logger import agent_logger

# Import tool functions directly (no decorators, no frameworks)
from tools.shell import execute_shell
from tools.web_request import send_http_request
from tools.file_system import read_file, write_file
from tools.scanner import scan_target
from tools.crypto import decode_string

console = Console()

# ── Tool Registry ────────────────────────────────────────────────────────────
TOOL_MAP = {
    "execute_shell": execute_shell,
    "send_http_request": send_http_request,
    "read_file": read_file,
    "write_file": write_file,
    "scan_target": scan_target,
    "decode_string": decode_string,
}

TOOL_NAMES = list(TOOL_MAP.keys()) + ["final_answer"]

# ── JSON Schema for Constrained Decoding ─────────────────────────────────────
# Ollama converts this to a GBNF grammar and masks invalid tokens at the logit
# level. The model CANNOT produce output that doesn't match this schema.
TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "thought": {
            "type": "string",
        },
        "tool": {
            "type": "string",
            "enum": TOOL_NAMES,
        },
        "input": {
            "type": "string",
        }
    },
    "required": ["thought", "tool", "input"]
}

# ── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an autonomous penetration testing AI agent on Kali Linux.

CRITICAL: You MUST use the EXACT target IP, URL, or domain from the user's message. Never substitute your own target.

AVAILABLE TOOLS:
- execute_shell: Run ANY shell command (nmap, curl, sqlmap, gobuster, nikto, hydra, ping, etc.)
- send_http_request: Fetch a webpage URL and extract its visible text
- read_file: Read a local file's contents
- write_file: Write content to a file (input format: filepath|content)
- scan_target: Quick nmap service scan on an IP or domain
- decode_string: Decode Base64, Hex, or URL-encoded strings
- final_answer: Report your findings and end the session

RULES:
1. ALWAYS extract the target from the user's request. NEVER invent or change the target.
2. For ping, ALWAYS add -c 4 to prevent hanging.
3. NEVER simulate or imagine tool output. Wait for the real Observation.
4. Chain multiple tools to thoroughly investigate.
5. Use final_answer when you have enough information to report.

EXAMPLE:
User: "ping {TARGET}" -> {"thought": "User wants to ping {TARGET}", "tool": "execute_shell", "input": "ping -c 4 {TARGET}"}
User: "scan {TARGET}" -> {"thought": "Running nmap on {TARGET}", "tool": "execute_shell", "input": "nmap -sV -F {TARGET}"}"""


class Agent:
    """
    Autonomous ReAct agent that uses Ollama's JSON Schema constrained
    decoding to guarantee valid, parseable tool-calling output.
    """

    def __init__(self, client, max_iterations=10):
        self.client = client
        self.max_iterations = max_iterations

    def run(self, user_input):
        """
        Run the autonomous agent loop.
        Returns the final answer string.
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]

        # Track previous actions to detect loops
        action_history = []

        for step in range(1, self.max_iterations + 1):
            console.print(f"\n[dim]{'─' * 20} Step {step}/{self.max_iterations} {'─' * 20}[/dim]")

            # ── Get LLM response ─────────────────────────────────────────
            try:
                if self.client.stream:
                    console.print("[dim italic]Streaming response...[/dim italic]")
                    raw = self.client.chat_stream(messages, TOOL_SCHEMA)
                else:
                    console.print("[dim italic]Thinking...[/dim italic]")
                    raw = self.client.chat(messages, TOOL_SCHEMA)
            except (ConnectionError, TimeoutError) as e:
                console.print(f"[bold red]Connection Error: {e}[/bold red]")
                return f"Agent failed: {e}"
            except Exception as e:
                agent_logger.error(f"LLM call failed: {e}")
                console.print(f"[bold red]LLM Error: {e}[/bold red]")
                return f"Agent failed: {e}"

            # ── Parse JSON response ──────────────────────────────────────
            try:
                response = json.loads(raw)
            except json.JSONDecodeError:
                console.print("[yellow]⚠ JSON parse error (retrying)...[/yellow]")
                agent_logger.warning(f"JSON parse failed on: {raw[:500]}")
                messages.append({"role": "assistant", "content": raw})
                messages.append({
                    "role": "user",
                    "content": "ERROR: Your response was not valid JSON. "
                               "Respond with a JSON object: {\"thought\": \"...\", \"tool\": \"...\", \"input\": \"...\"}"
                })
                continue

            thought = response.get("thought", "")
            tool = response.get("tool", "")
            tool_input = response.get("input", "")

            # ── Display the agent's decision ─────────────────────────────
            console.print(f"[bold cyan]💭 Thought:[/bold cyan] {thought}")
            console.print(f"[bold yellow]🔧 Tool:[/bold yellow] {tool}")
            if tool != "final_answer":
                console.print(f"[bold yellow]📥 Input:[/bold yellow] {tool_input}")

            # ── Check for final answer ───────────────────────────────────
            if tool == "final_answer":
                agent_logger.info(f"Agent completed in {step} steps.")
                return tool_input

            # ── Loop detection ───────────────────────────────────────────
            action_key = f"{tool}:{tool_input}"
            if action_key in action_history:
                console.print("[bold yellow]⚠ Loop detected — same action repeated. Nudging agent...[/bold yellow]")
                messages.append({"role": "assistant", "content": json.dumps(response)})
                messages.append({
                    "role": "user",
                    "content": f"STOP: You already ran {tool}('{tool_input[:80]}') and got the same result. "
                               "Do NOT repeat it. You MUST try a DIFFERENT tool or a DIFFERENT input. "
                               "Suggestions: try execute_shell with curl, nikto, gobuster, dirb, whatweb, or nmap. "
                               "Or use final_answer to report what you found so far."
                })
                continue
            action_history.append(action_key)

            # ── Execute tool ─────────────────────────────────────────────
            if tool not in TOOL_MAP:
                observation = f"ERROR: Unknown tool '{tool}'. Available: {', '.join(TOOL_MAP.keys())}"
            else:
                agent_logger.info(f"Executing: {tool}('{tool_input[:100]}')")
                try:
                    tool_fn = TOOL_MAP[tool]
                    observation = tool_fn(tool_input)
                except Exception as e:
                    observation = f"Tool execution error: {e}"
                    agent_logger.error(f"Tool error: {e}")

            # ── Display observation ──────────────────────────────────────
            display_obs = str(observation)
            if len(display_obs) > 2000:
                display_obs = display_obs[:2000] + "\n...[DISPLAY TRUNCATED]..."

            console.print(Panel(
                display_obs,
                title="[bold green]📡 Observation[/bold green]",
                border_style="green"
            ))

            # ── Feed observation back into conversation history ──────────
            messages.append({"role": "assistant", "content": json.dumps(response)})
            messages.append({
                "role": "user",
                "content": f"Observation from {tool}:\n{str(observation)[:3000]}\n\n"
                           "Based on this output, what is your NEXT different action? "
                           "Do NOT repeat the same command. Try a different tool or approach."
            })

        # Max iterations reached
        agent_logger.warning("Agent hit max iterations.")
        return "Agent reached maximum iterations. Review the observations above for partial results."

