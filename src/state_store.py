from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from src.utils.logger import get_logger


logger = get_logger("state")


@dataclass
class StateStore:
    """Mantem historico de desafios completos e falhos."""
    path: Path
    data: Dict[str, List[dict]] = field(default_factory=lambda: {"completed": [], "failed": []})

    def load(self) -> None:
        """Carrega state.json se existir."""
        if not self.path.exists():
            self.save()
            return
        with self.path.open("r", encoding="utf-8") as handle:
            self.data = json.load(handle)

    def save(self) -> None:
        """Salva state.json."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=2, ensure_ascii=False)

    def is_completed(self, problem_id: str) -> bool:
        """Checa se problema ja foi concluido."""
        return any(item["problem_id"] == problem_id for item in self.data.get("completed", []))

    def mark_completed(self, record: dict) -> None:
        """Registra desafio concluido."""
        logger.info("✅ Registrando desafio como concluido")
        self.data.setdefault("completed", []).append(record)
        self.save()

    def mark_failed(self, record: dict) -> None:
        """Registra falha."""
        logger.error("🚨 Registrando falha de desafio")
        self.data.setdefault("failed", []).append(record)
        self.save()
