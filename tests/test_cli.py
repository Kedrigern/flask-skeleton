from my_web.app import help, run


def test_help(capsys):
    help()
    captured = capsys.readouterr()
    for word in ["Usage:", "uv run web", "uv run shell", "uv run help"]:
        assert word in captured.out
