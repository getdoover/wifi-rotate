from pathlib import Path

from pydoover import config


class WifiProfile(config.Object):
    ssid = config.String("SSID", description="The SSID (name) of the wifi network")
    password = config.String(
        "Password", description="The password for the wifi network"
    )
    hold_time = config.Integer(
        "Hold Time",
        default=180,
        description="The time in seconds to hold on to the wifi network before rotating",
    )

    def __init__(self, display_name: str = "Wifi Profile"):
        super().__init__(
            display_name, description="The wifi profile to rotate through"
        )


class WifiRotateConfig(config.Schema):
    profiles = config.Array("Profiles", element=WifiProfile())


def export():
    WifiRotateConfig().export(Path(__file__).parents[2] / "doover_config.json", "wifi_rotate")


if __name__ == "__main__":
    export()
