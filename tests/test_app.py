from my_web.app import create_app, run
from flask import Flask
from typing import Callable

def test_main():
    assert isinstance(run, Callable)

def test_app():
    app = create_app()
    assert isinstance(app, Flask)
