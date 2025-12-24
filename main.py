from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from src.git_client import GitClient
from src.providers.codeforces import CodeforcesProvider
from src.repo_writer import RepoWriter
from src.scheduler import Scheduler
from src.settings import Settings
from src.solver.template_solver import TemplateSolver
from src.state_store import StateStore
from src.utils.logger import get_logger


logger = get_logger("main")


def build_scheduler(settings_path: Path) -> Scheduler:
    """Constroi o Scheduler e dependencias."""
    settings = Settings.load(str(settings_path))
    repo_path = Path(settings.repo_path)
    state_store = StateStore(path=repo_path / "state" / "state.json")
    provider = CodeforcesProvider()
    solver = TemplateSolver()
    writer = RepoWriter(repo_path=repo_path)
    git_client = GitClient(repo_path=repo_path, remote=settings.git_remote, branch=settings.git_branch)
    return Scheduler(
        settings=settings,
        state_store=state_store,
        provider=provider,
        solver=solver,
        writer=writer,
        git_client=git_client,
    )


def pick_job(settings: Settings, day: str | None, time_str: str | None):
    """Seleciona job por dia/horario (opcional)."""
    if not day:
        return None
    jobs = settings.schedule.get(day.lower())
    if not jobs:
        raise RuntimeError(f"Nenhum job para o dia {day}")
    if not time_str:
        return jobs[0]
    for job in jobs:
        if job.time == time_str:
            return job
    raise RuntimeError(f"Nenhum job em {day} {time_str}")


def main() -> None:
    """CLI principal."""
    load_dotenv()
    parser = argparse.ArgumentParser(description="AutoFeedr V2 - Codeforces Scheduler")
    parser.add_argument("--settings", default="settings.json", help="Caminho do settings.json")
    sub = parser.add_subparsers(dest="command", required=True)

    run_once = sub.add_parser("run_once", help="Executa um job imediato")
    run_once.add_argument("--day", help="Dia da semana (opcional)")
    run_once.add_argument("--time", help="Horario HH:MM (opcional)")

    sub.add_parser("run_scheduler", help="Executa o loop do scheduler")

    args = parser.parse_args()
    scheduler = build_scheduler(Path(args.settings))

    if args.command == "run_once":
        settings = Settings.load(args.settings)
        job = pick_job(settings, args.day, args.time)
        scheduler.run_once(job=job)
    else:
        scheduler.run_scheduler()


if __name__ == "__main__":
    main()
