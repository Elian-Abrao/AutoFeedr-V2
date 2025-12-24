from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from src.providers.base import Problem
from src.utils.logger import get_logger


logger = get_logger("solver")


@dataclass
class GeneratedArtifacts:
    readme: str
    solution: str
    tests: str
    notes: str


class TemplateSolver:
    """Gera artefatos baseline com templates e TODOs."""
    def generate(self, problem: Problem, language: str) -> GeneratedArtifacts:
        """Cria readme, solution, tests e notes."""
        if language != "python":
            raise ValueError("Linguagem ainda nao suportada no modo baseline")
        logger.info("🧩 Gerando artefatos baseline para o desafio")
        readme = self._build_readme(problem)
        solution = self._build_solution(problem)
        tests = self._build_tests(problem)
        notes = self._build_notes(problem)
        return GeneratedArtifacts(readme=readme, solution=solution, tests=tests, notes=notes)

    def _build_readme(self, problem: Problem) -> str:
        """Monta README em primeira pessoa com metadados."""
        lines = [
            f"# {problem.name}",
            "",
            "## Contexto do desafio",
            f"- Fonte: Codeforces",
            f"- Link: {problem.url}",
            f"- Rating: {problem.rating or 'N/A'}",
            f"- Tags: {', '.join(problem.tags) if problem.tags else 'N/A'}",
            "",
            "## Resumo do enunciado",
            "A API do Codeforces nao fornece o statement completo. Estou registrando",
            "apenas o link oficial e os metadados disponiveis.",
            "",
            "## Minha abordagem",
            "Ainda nao gerei uma solucao final. Este arquivo foi criado por um template",
            "baseline aguardando a integracao com o gerador LLM.",
            "",
            "## Passo a passo",
            "1) Ler a entrada conforme o enunciado oficial.",
            "2) Aplicar a estrategia planejada para o problema.",
            "3) Produzir a saida formatada.",
            "",
            "## Complexidade",
            "- Tempo: TBD",
            "- Memoria: TBD",
            "",
            "## Casos de borda",
            "- TBD",
        ]
        return "\n".join(lines)

    def _build_solution(self, problem: Problem) -> str:
        """Gera solution.py placeholder."""
        return "\n".join(
            [
                '"""',
                f"Problema: {problem.name}",
                f"Link: {problem.url}",
                "",
                "TODO: Integrar solver com LLM para gerar solucao real.",
                '"""',
                "",
                "import sys",
                "",
                "",
                "def solve() -> None:",
                "    data = sys.stdin.read().strip()",
                "    if not data:",
                "        return",
                "    # TODO: implementar solucao",
                "    print('TODO')",
                "",
                "",
                "if __name__ == '__main__':",
                "    solve()",
            ]
        )

    def _build_tests(self, problem: Problem) -> str:
        """Cria pytest baseline para smoke test."""
        return "\n".join(
            [
                "import pytest",
                "",
                "",
                "def test_smoke_import():",
                "    # Smoke test para garantir que o arquivo existe e importa.",
                "    import solution  # noqa: F401",
                "",
                "",
                "@pytest.mark.skip(reason='Template baseline aguardando solucao real')",
                "def test_placeholder():",
                "    assert True",
            ]
        )

    def _build_notes(self, problem: Problem) -> str:
        """Gera notes.md com bullets de aprendizado."""
        notes = [
            "- Li o enunciado no link oficial antes de propor uma estrategia.",
            "- Defini um plano de leitura e escrita de entrada/saida.",
            "- Separei pontos de possiveis otimizações.",
            "- TODO: registrar insights quando a solucao real estiver pronta.",
        ]
        return "\n".join(notes)
