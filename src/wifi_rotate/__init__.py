from pydoover.docker import run_app

from .application import WifiRotateApplication

def main():
    """
    Run the application.
    """
    run_app(WifiRotateApplication())
