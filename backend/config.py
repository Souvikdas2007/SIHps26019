"""Environment-driven local application configuration."""

from dataclasses import dataclass
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    app_env: str
    database_path: Path
    llm_provider: str
    llm_runtime: str
    llama_cpp_base_url: str
    llama_cpp_model: str
    embedding_provider: str
    embedding_model: str
    rag_enabled: bool
    auth_enabled: bool
    cors_origins: tuple[str, ...]

    @classmethod
    def from_environment(cls) -> "Settings":
        app_env = os.getenv("APP_ENV", "local").strip().lower()
        cors_origins = tuple(
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
            ).split(",")
            if origin.strip()
        )
        if app_env not in {"local", "test", "staging", "production"}:
            raise ValueError("APP_ENV must be local, test, staging or production")
        if app_env == "production":
            if not cors_origins or any(
                origin == "*" or not origin.startswith("https://")
                for origin in cors_origins
            ):
                raise ValueError("Production CORS_ORIGINS must contain only explicit HTTPS origins")
        return cls(
            app_env=app_env,
            database_path=_sqlite_path(os.getenv("DATABASE_URL", "sqlite:///./database/ps26019.db")),
            llm_provider=os.getenv("LLM_PROVIDER", "local"),
            llm_runtime=os.getenv("LLM_RUNTIME", "llama.cpp"),
            llama_cpp_base_url=os.getenv("LLAMA_CPP_BASE_URL", "http://127.0.0.1:8080"),
            llama_cpp_model=os.getenv("LLAMA_CPP_MODEL", "local-model.gguf"),
            embedding_provider=os.getenv("EMBEDDING_PROVIDER", "local"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "local-embedding-model"),
            rag_enabled=_as_bool(os.getenv("RAG_ENABLED", "true")),
            auth_enabled=_as_bool(os.getenv("AUTH_ENABLED", "true")),
            cors_origins=cors_origins,
        )


def _sqlite_path(database_url: str) -> Path:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise ValueError("DATABASE_URL must use the sqlite:/// scheme")

    path = Path(database_url[len(prefix):])
    return path if path.is_absolute() else PROJECT_ROOT / path


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}
