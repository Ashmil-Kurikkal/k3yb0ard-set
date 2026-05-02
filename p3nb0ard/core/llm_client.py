import os
import json
import requests
from core.logger import agent_logger


class OllamaClient:
    """
    Thin HTTP client for Ollama's /api/chat endpoint.
    No frameworks, no Pydantic — just raw HTTP + JSON.
    """

    def __init__(self, stream=False):
        self.base_url = os.environ.get("HOST_OLLAMA_IP", "http://127.0.0.1:11434")
        self.model = os.environ.get("OLLAMA_MODEL", "WhiteRabbitNeo/Llama-3.1-WhiteRabbitNeo-2-8B")
        self.stream = stream
        agent_logger.info(f"Ollama client: model={self.model}, base={self.base_url}, stream={self.stream}")

    def _build_payload(self, messages, format_schema=None, stream=False):
        """Build the JSON payload for Ollama /api/chat."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": 0.1,
                "num_predict": 4096,
            }
        }
        if format_schema:
            payload["format"] = format_schema
        return payload

    def chat(self, messages, format_schema=None):
        """
        Non-streaming chat. Sends messages to Ollama and returns the
        assistant's response content as a string.
        """
        payload = self._build_payload(messages, format_schema, stream=False)

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=300
            )
            response.raise_for_status()
        except requests.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Is Ollama running? Is the IP correct in your .env file?"
            )
        except requests.Timeout:
            raise TimeoutError("Ollama request timed out after 300 seconds.")

        data = response.json()
        content = data["message"]["content"]
        agent_logger.debug(f"LLM response: {content[:200]}")
        return content

    def chat_stream(self, messages, format_schema=None):
        """
        Streaming chat. Sends messages to Ollama, prints tokens in real-time,
        and returns the full assembled response content as a string.
        """
        payload = self._build_payload(messages, format_schema, stream=True)

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True,
                timeout=300
            )
            response.raise_for_status()
        except requests.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Is Ollama running? Is the IP correct in your .env file?"
            )

        full_content = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if "message" in chunk and "content" in chunk["message"]:
                    token = chunk["message"]["content"]
                    full_content += token
                    # Print each token as it arrives for real-time feedback
                    print(token, end="", flush=True)
        print()  # Newline after stream completes

        agent_logger.debug(f"LLM streamed response: {full_content[:200]}")
        return full_content
