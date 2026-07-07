"""
Basic tests for an application.

This ensures all modules are importable and that the config is valid.
"""

def test_import_app():
    from wifi_rotate.application import WifiRotateApplication
    assert WifiRotateApplication

def test_config():
    from wifi_rotate.app_config import WifiRotateConfig

    schema = WifiRotateConfig.to_schema()
    assert isinstance(schema, dict)
    assert len(schema["properties"]) > 0