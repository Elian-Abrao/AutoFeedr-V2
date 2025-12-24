from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.utils.logger import get_logger


logger = get_logger("git")


@dataclass
class GitClient:
    """Wrapper simples para git CLI com tratamento de erro."""
    repo_path: Path
    remote: Optional[str]
    branch: str

    def _run(self, args: list[str]) -> None:
        """Executa um comando git dentro do repo."""
        logger.info(f"🔧 Executando git: {' '.join(args)}")
        result = subprocess.run(
            args,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=False,
            env=os.environ.copy(),
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"git failed: {result.stdout}\n{result.stderr}"
            )

    def add_all(self) -> None:
        """Stage de todos os arquivos."""
        self._run(["git", "add", "."])

    def commit(self, message: str) -> None:
        """Cria commit local."""
        self._run(["git", "commit", "-m", message])

    def push(self) -> None:
        """Faz push para o remoto configurado."""
        if not self.remote:
            logger.warning("⚠️ git_remote nao definido, pulando push")
            return
        self._run(["git", "push", self.remote, self.branch])
