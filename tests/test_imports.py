"""
Basic tests for an application.

This ensures all modules are importable and that the config is valid.
"""

def test_import_app():
    from wifi_rotate.application import WifiRotateApplication
    assert WifiRotateApplication

def test_config():
    from wifi_rotate.app_config import WifiRotateConfig

    config = WifiRotateConfig()
    assert isinstance(config.to_dict(), dict)