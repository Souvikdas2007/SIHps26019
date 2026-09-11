"""Provider contract for local and optional future LLM runtimes."""

from dataclasses import dataclass
from typing import Protocol


class LLMProvider(Protocol):
    def generate(self, prompt: str, context: dict) -> str:
        """Generate text using the provider with supplied context."""

    def health(self) -> bool:
        """Return whether the provider is reachable and configured."""


@dataclass(frozen=True)
class AIAvailability:
    available: bool
    provider: str
    message: str
