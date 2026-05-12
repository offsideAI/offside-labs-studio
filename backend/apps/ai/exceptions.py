class AIClientError(Exception):
    """Raised by apps.ai.client when an LLM call fails for any reason."""


class AIResponseError(Exception):
    """Raised when the LLM returns a response that fails our shape checks."""
