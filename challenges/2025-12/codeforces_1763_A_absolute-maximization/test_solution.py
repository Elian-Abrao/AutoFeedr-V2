import pytest


def test_smoke_import():
    # Smoke test para garantir que o arquivo existe e importa.
    import solution  # noqa: F401


@pytest.mark.skip(reason='Template baseline aguardando solucao real')
def test_placeholder():
    assert True