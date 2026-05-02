import os


def read_file(file_path: str) -> str:
    """
    Safely reads the contents of a local file.
    Input must be an absolute or relative path to a file.
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
            
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        if len(content) > 3000:
            return content[:3000] + "\n...[OUTPUT TRUNCATED]..."
        return content
    except PermissionError:
        return f"Error: Permission denied reading {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(args: str) -> str:
    """
    Writes data to a local file. Useful for creating exploit scripts or wordlists.
    Input MUST be a string formatted exactly as: <file_path>|<content>
    Example: exploit.py|print('hacked')
    """
    try:
        if "|" not in args:
            return "Error: Input must be formatted as <file_path>|<content>"
            
        parts = args.split("|", 1)
        file_path = parts[0].strip()
        content = parts[1]
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return f"Successfully wrote {len(content)} bytes to {file_path}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"
