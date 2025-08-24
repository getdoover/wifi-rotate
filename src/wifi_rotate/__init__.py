from pydoover.docker import run_app

from .application import WifiRotateApplication
from .app_config import WifiRotateConfig

def main():
    """
    Run the application.
    """
    run_app(WifiRotateApplication(config=WifiRotateConfig()))
