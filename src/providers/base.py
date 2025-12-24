from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Protocol, Tuple


@dataclass
class Problem:
    source: str
    contest_id: int
    index: str
    name: str
    rating: Optional[int]
    tags: List[str]
    url: str

    @property
    def problem_id(self) -> str:
        return f"{self.source}:{self.contest_id}:{self.index}"

    @property
    def slug(self) -> str:
        safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in self.name).strip("-")
        while "--" in safe:
            safe = safe.replace("--", "-")
        return safe or f"{self.contest_id}{self.index}".lower()


class ProblemProvider(Protocol):
    """Contrato para provedores de desafios."""

    def fetch_problem(
        self,
        difficulty: Optional[str],
        rating_range: Optional[Tuple[int, int]],
        tags: Optional[List[str]],
        used_ids: List[str],
    ) -> Problem:
        ...
