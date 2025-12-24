from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from src.git_client import GitClient
from src.providers.base import Problem
from src.providers.codeforces import CodeforcesProvider
from src.repo_writer import RepoWriter
from src.settings import JobSettings, Settings
from src.solver.template_solver import TemplateSolver
from src.state_store import StateStore
from src.utils.logger import get_logger
from src.utils.time import WEEKDAYS, next_datetime_for, now_in_tz


logger = get_logger("scheduler")


@dataclass
class Scheduler:
    """Agenda e executa jobs com base no settings.json."""
    settings: Settings
    state_store: StateStore
    provider: CodeforcesProvider
    solver: TemplateSolver
    writer: RepoWriter
    git_client: GitClient

    def run_once(self, job: Optional[JobSettings] = None) -> None:
        """Executa um unico job imediatamente."""
        logger.info("🚀 Rodando job unico")
        target_job = job or self._pick_first_job()
        self._execute_job(target_job)

    def run_scheduler(self) -> None:
        """Loop infinito que aguarda o proximo horario agendado."""
        logger.info("🕒 Iniciando loop de scheduler")
        while True:
            next_job, next_time = self._get_next_job()
            wait_seconds = max(0, (next_time - now_in_tz(self.settings.timezone)).total_seconds())
            logger.info(f"⏳ Proximo job em {int(wait_seconds)}s ({next_time.isoformat()})")
            time.sleep(wait_seconds)
            self._execute_job(next_job)

    def _pick_first_job(self) -> JobSettings:
        """Seleciona o primeiro job configurado."""
        for day in WEEKDAYS:
            if day in self.settings.schedule and self.settings.schedule[day]:
                return self.settings.schedule[day][0]
        raise RuntimeError("Nenhum job encontrado no schedule")

    def _get_next_job(self) -> Tuple[JobSettings, datetime]:
        """Calcula o proximo job e horario futuro."""
        now = now_in_tz(self.settings.timezone)
        candidates: list[tuple[JobSettings, datetime]] = []
        for day, jobs in self.settings.schedule.items():
            for job in jobs:
                run_at = next_datetime_for(day, job.time, self.settings.timezone, now)
                candidates.append((job, run_at))
        candidates.sort(key=lambda item: item[1])
        return candidates[0]

    def _execute_job(self, job: JobSettings) -> None:
        """Executa o fluxo completo: provider, solver, testes e git."""
        self.state_store.load()
        used = [item["problem_id"] for item in self.state_store.data.get("completed", [])]
        last_error: Exception | None = None
        for attempt in range(self.settings.max_retries + 1):
            try:
                problem = self.provider.fetch_problem(
                    difficulty=job.difficulty,
                    rating_range=job.rating_range,
                    tags=job.tags,
                    used_ids=used,
                )
                artifacts = self.solver.generate(problem, job.language)
                challenge_dir = self.writer.write_problem(problem, artifacts, self.settings.timezone)
                self._run_tests(challenge_dir)
                self.git_client.add_all()
                commit_msg = self._format_commit_message(job, problem)
                self.git_client.commit(commit_msg)
                self.git_client.push()
                self.state_store.mark_completed(
                    {
                        "problem_id": problem.problem_id,
                        "source": problem.source,
                        "contest_id": problem.contest_id,
                        "index": problem.index,
                        "slug": problem.slug,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                logger.info("✅ Job finalizado com sucesso")
                return
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt < self.settings.max_retries:
                    wait_seconds = self.settings.backoff_seconds * (2**attempt)
                    logger.warning(f"⚠️ Tentativa {attempt + 1} falhou, retry em {wait_seconds}s")
                    time.sleep(wait_seconds)
                    continue
                logger.error(f"🚨 Job falhou: {exc}")
                self.state_store.mark_failed(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "error": str(exc),
                        "job": job.model_dump(),
                    }
                )
        return

    def _run_tests(self, challenge_dir: Path) -> None:
        """Roda pytest somente no diretorio do desafio."""
        logger.info("🧪 Rodando testes pytest")
        result = subprocess.run(
            ["pytest", str(challenge_dir)],
            capture_output=True,
            text=True,
            check=False,
            cwd=self.settings.repo_path,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pytest falhou:\n{result.stdout}\n{result.stderr}")

    def _format_commit_message(self, job: JobSettings, problem: Problem) -> str:
        """Renderiza a mensagem de commit conforme template."""
        template = job.commit_message_template or "chore(cf): add {slug}"
        return template.format(
            slug=problem.slug,
            difficulty=job.difficulty or "rating",
            contest_id=problem.contest_id,
            index=problem.index,
            source=problem.source,
        )
