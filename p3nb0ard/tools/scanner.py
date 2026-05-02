import re
import subprocess


def scan_target(target: str) -> str:
    """
    Executes a fast nmap scan against a target IP or domain.
    Input must be a valid IP address or domain name.
    """
    # Extremely strict regex to prevent command injection via this tool
    # (Though we have the shell tool, it's good practice to sanitize wrappers)
    ip_domain_regex = r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$|^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    
    if not re.match(ip_domain_regex, target):
        return "Error: Invalid target format. Must be an IP address or domain."

    try:
        # Fast scan, no ping, service version detection
        result = subprocess.run(
            ["nmap", "-sV", "-F", "-Pn", target],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout
        
        if len(output) > 3000:
            return output[:3000] + "\n...[OUTPUT TRUNCATED]..."
        return output
    except FileNotFoundError:
        return "Error: nmap is not installed or not in PATH."
    except Exception as e:
        return f"Error running nmap: {str(e)}"
