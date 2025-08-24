from pathlib import Path

from pydoover import config


class WifiRotateConfig(config.Schema):
    def __init__(self):
        # self.wifi_interface = config.String("Wifi Interface", default="wlan0")

        profile = self.construct_wifi_profile()
        self.profiles = config.Array("Profiles", element=profile)

    def construct_wifi_profile(self):
        wifi_profile = config.Object("Wifi Profile", description="The wifi profile to rotate through")
        wifi_profile.add_elements(
            config.String("SSID", description="The SSID (name) of the wifi network"),
            config.String("Password", description="The password for the wifi network"),
            config.Integer("Hold Time", default=180, description="The time in seconds to hold on to the wifi network before rotating"),
            # config.Integer("Connect Timeout", default=30, description="The timeout in seconds to connect to the wifi network"),
        )
        return wifi_profile


def export():
    WifiRotateConfig().export(Path(__file__).parents[2] / "doover_config.json", "wifi_rotate")

if __name__ == "__main__":
    export()
