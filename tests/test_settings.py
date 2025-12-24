from src.settings import Settings


def test_settings_load():
    settings = Settings.load("settings.json")
    assert settings.repo_path
