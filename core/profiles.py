"""Replaceable profile contracts for unresolved project choices."""

from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence


@dataclass(frozen=True)
class VersionedProfile:
    identifier: str
    version: str
    display_name: str


@dataclass(frozen=True)
class DatasetProfile(VersionedProfile):
    source: str
    source_url: str | None
    data_year: int | None
    crs: str | None
    asset_path: str


@dataclass(frozen=True)
class ScenarioConfig(VersionedProfile):
    factors: Sequence[str]
    weights: Mapping[str, float]
    assumptions: Sequence[str]


class StudyAreaProvider(Protocol):
    def get_profile(self, identifier: str, version: str) -> VersionedProfile:
        """Return a versioned study-area profile."""


class SpatialUnitProvider(Protocol):
    def get_profile(self, identifier: str, version: str) -> VersionedProfile:
        """Return a versioned simulation spatial-unit profile."""


class ValidationStrategy(Protocol):
    def validate(self, profile: VersionedProfile) -> Sequence[str]:
        """Return validation findings; an empty sequence means valid."""


class EmbeddingProvider(Protocol):
    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        """Create local embeddings without coupling callers to a model."""


class AuthProvider(Protocol):
    def authenticate(self, username: str, secret: str) -> bool:
        """Authenticate through the configured local implementation."""
