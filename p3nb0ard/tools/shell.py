import subprocess


def execute_shell(command: str) -> str:
    """
    Executes a shell command on the local Kali Linux system.
    Use this to run hacker tools like sqlmap, gobuster, nikto, nmap, curl, etc.
    Returns the standard output or error. If the output is too long, it truncates it.
    Input must be a valid shell command string.
    """
    try:
        # We use shell=True to allow complex bash commands (pipes, redirects)
        # Note: This is an uncensored agent running locally, so this is intentional.
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120 # Prevent infinite hangs
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
            
        if not output.strip():
            return "Command executed successfully with no output."
            
        # Truncate to avoid blowing up the context window for small models
        if len(output) > 3000:
            return output[:3000] + "\n...[OUTPUT TRUNCATED]..."
            
        return output
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 120 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"
