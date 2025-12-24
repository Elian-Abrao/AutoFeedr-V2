from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from src.providers.base import Problem
from src.solver.template_solver import GeneratedArtifacts
from src.utils.logger import get_logger


logger = get_logger("writer")


@dataclass
class RepoWriter:
    """Escreve a estrutura de pastas e atualiza o indice."""
    repo_path: Path

    def write_problem(self, problem: Problem, artifacts: GeneratedArtifacts, tz_name: str) -> Path:
        """Cria a pasta do desafio e salva os arquivos."""
        logger.info("📝 Criando estrutura de pastas do desafio")
        now = datetime.now(ZoneInfo(tz_name))
        month_folder = now.strftime("%Y-%m")
        challenge_dir = (
            self.repo_path
            / "challenges"
            / month_folder
            / f"{problem.source}_{problem.contest_id}_{problem.index}_{problem.slug}"
        )
        challenge_dir.mkdir(parents=True, exist_ok=True)
        (challenge_dir / "README.md").write_text(artifacts.readme, encoding="utf-8")
        (challenge_dir / "solution.py").write_text(artifacts.solution, encoding="utf-8")
        (challenge_dir / "test_solution.py").write_text(artifacts.tests, encoding="utf-8")
        (challenge_dir / "notes.md").write_text(artifacts.notes, encoding="utf-8")
        self._update_index(problem, challenge_dir)
        return challenge_dir

    def _update_index(self, problem: Problem, challenge_dir: Path) -> None:
        """Acrescenta o desafio ao INDEX.md."""
        index_path = self.repo_path / "INDEX.md"
        if not index_path.exists():
            index_path.write_text("# Desafios\n", encoding="utf-8")
        rel_path = challenge_dir.relative_to(self.repo_path)
        line = f"- [{problem.name}]({rel_path.as_posix()})\n"
        with index_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
