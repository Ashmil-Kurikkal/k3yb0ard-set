import requests
from bs4 import BeautifulSoup


def send_http_request(url: str) -> str:
    """
    Sends a basic HTTP GET request to a URL and returns the text content.
    For complex web interactions (POST, custom headers, SQLi), prefer using 
    the execute_shell tool with curl or sqlmap.
    This tool is best for quickly reading the HTML of a webpage.
    Input must be a valid URL starting with http:// or https://.
    """
    try:
        if not url.startswith("http"):
            url = "http://" + url
            
        # Disable warnings for self-signed certificates in CTFs
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        response = requests.get(url, verify=False, timeout=10)
        
        # Try to parse with BeautifulSoup to reduce noise
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove scripts and styles for LLM context optimization
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        output = f"Status Code: {response.status_code}\nHeaders: {dict(response.headers)}\n\nExtracted Text:\n{text}"
        
        if len(output) > 3000:
            return output[:3000] + "\n...[OUTPUT TRUNCATED]..."
        return output
    except Exception as e:
        return f"Error connecting to {url}: {str(e)}"
