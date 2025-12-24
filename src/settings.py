from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, field_validator, model_validator


class JobSettings(BaseModel):
    """Config de um job individual."""
    time: str = Field(..., description="HH:MM")
    difficulty: Optional[str] = Field(default=None, description="easy|medium|hard")
    rating_range: Optional[Tuple[int, int]] = None
    tags: Optional[List[str]] = None
    language: str = Field(default="python")
    commit_message_template: Optional[str] = None

    @field_validator("time")
    @classmethod
    def validate_time(cls, value: str) -> str:
        parts = value.split(":")
        if len(parts) != 2:
            raise ValueError("time must be HH:MM")
        hour, minute = parts
        if not (hour.isdigit() and minute.isdigit()):
            raise ValueError("time must be HH:MM")
        if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
            raise ValueError("time must be HH:MM")
        return value

    @model_validator(mode="after")
    def validate_difficulty_or_rating(self):
        if not self.difficulty and not self.rating_range:
            raise ValueError("job must set difficulty or rating_range")
        return self


class Settings(BaseModel):
    """Config principal do sistema."""
    repo_path: str
    git_remote: Optional[str] = None
    git_branch: str = "main"
    timezone: str = "America/Sao_Paulo"
    max_retries: int = 2
    backoff_seconds: int = 10
    schedule: Dict[str, List[JobSettings]]

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, value: Dict[str, List[JobSettings]]):
        """Garante que exista ao menos um job."""
        if not value:
            raise ValueError("schedule cannot be empty")
        return value

    @classmethod
    def load(cls, path: str) -> "Settings":
        """Carrega settings.json."""
        import json

        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return cls.model_validate(payload)
