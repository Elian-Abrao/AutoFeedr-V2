# AutoFeedr V2

Serviço programado que busca desafios do Codeforces, gera solução em Python, cria testes pytest e faz commit/push em um repositório configurado.

## Visão geral
1) Scheduler detecta o próximo job do `settings.json`.
2) Codeforces Provider seleciona um problema por dificuldade/tags.
3) Solver gera `solution.py`, `README.md` e `notes.md` (modo baseline com templates).
4) RepoWriter cria a estrutura e atualiza `INDEX.md`.
5) Pytest roda localmente.
6) GitClient faz commit e push (somente se os testes passarem).

## Requisitos
- Python 3.10+
- Git instalado e configurado no sistema

## Instalação
```bash
pip install -r requirements.txt
```

Crie um `.env` se quiser usar variáveis de ambiente (ex.: token do git).

## Configuração
Edite `settings.json` com o repo alvo, timezone e agenda.

## Execução
Modo único (testes rápidos):
```bash
python main.py run_once
```

Modo agendado:
```bash
python main.py run_scheduler
```

## Estrutura
- `src/` código do serviço
- `challenges/` desafios gerados
- `state/state.json` histórico e anti-repetição
- `INDEX.md` índice dos desafios
- `settings.json` configuração principal

## Docker
Veja `Dockerfile` e `docker-compose.yml`.
