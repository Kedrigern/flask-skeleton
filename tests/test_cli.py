from my_web.app import app_help


def test_help(capsys):
    app_help()
    captured = capsys.readouterr()
    for word in ["Usage:", "uv run web", "uv run shell", "uv run help"]:
        assert word in captured.out
