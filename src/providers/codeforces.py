from __future__ import annotations

import random
from typing import List, Optional, Tuple

import requests

from src.utils.logger import get_logger
from src.providers.base import Problem


logger = get_logger("codeforces")


DIFFICULTY_MAP = {
    "easy": (800, 1200),
    "medium": (1300, 1700),
    "hard": (1800, 2300),
}


class CodeforcesProvider:
    """Provider baseado na API publica do Codeforces."""
    base_url = "https://codeforces.com/api/problemset.problems"

    def fetch_problem(
        self,
        difficulty: Optional[str],
        rating_range: Optional[Tuple[int, int]],
        tags: Optional[List[str]],
        used_ids: List[str],
    ) -> Problem:
        """Busca e seleciona um problema valido segundo filtros."""
        rating_from, rating_to = self._resolve_rating(difficulty, rating_range)
        params = {}
        if tags:
            params["tags"] = ";".join(tags)
        logger.info("🧠 Buscando problemas no Codeforces")
        resp = requests.get(self.base_url, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("status") != "OK":
            raise RuntimeError(f"Codeforces API error: {payload}")
        problems = payload["result"]["problems"]
        filtered = []
        for problem in problems:
            rating = problem.get("rating")
            if rating is None:
                continue
            if rating_from and rating < rating_from:
                continue
            if rating_to and rating > rating_to:
                continue
            contest_id = problem.get("contestId")
            index = problem.get("index")
            if not contest_id or not index:
                continue
            pid = f"codeforces:{contest_id}:{index}"
            if pid in used_ids:
                continue
            filtered.append(problem)
        if not filtered:
            raise RuntimeError("Nenhum problema encontrado com os filtros atuais")
        chosen = random.choice(filtered)
        contest_id = chosen["contestId"]
        index = chosen["index"]
        url = f"https://codeforces.com/problemset/problem/{contest_id}/{index}"
        return Problem(
            source="codeforces",
            contest_id=contest_id,
            index=index,
            name=chosen.get("name", f"CF {contest_id}{index}"),
            rating=chosen.get("rating"),
            tags=chosen.get("tags", []),
            url=url,
        )

    def _resolve_rating(
        self,
        difficulty: Optional[str],
        rating_range: Optional[Tuple[int, int]],
    ) -> Tuple[Optional[int], Optional[int]]:
        """Resolve difficulty para faixa de rating."""
        if rating_range:
            return rating_range[0], rating_range[1]
        if difficulty:
            return DIFFICULTY_MAP.get(difficulty.lower(), (None, None))
        return None, None
