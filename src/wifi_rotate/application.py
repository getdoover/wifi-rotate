import logging
import time
import nmcli
import traceback

from pydoover.docker import Application

from .app_config import WifiRotateConfig
from .app_tags import WifiRotateTags

log = logging.getLogger()

class WifiRotateApplication(Application):
    config_cls = WifiRotateConfig
    tags_cls = WifiRotateTags

    config: WifiRotateConfig  # not necessary, but helps your IDE provide autocomplete!
    tags: WifiRotateTags

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.loop_target_period = 5 # seconds
        self.started: float = time.time()

        self.current_profile_index = 0
        self.last_wifi_change = time.time()
        # SSID we're actually connected to (set only on a successful connect),
        # published as a tag so co-located meter apps only poll their own AP.
        self.connected_ssid = None

    async def setup(self):
        if len(self.profiles) == 0:
            log.error("No wifi profiles configured")
            return
        
        nmcli.disable_use_sudo()
        # Connect to the first profile
        await self.rotate_to_next_wifi_profile(increment=False)

    async def main_loop(self):
        if len(self.profiles) == 0:
            log.error("No wifi profiles configured")
            return
        
        if self.time_until_next_profile <= 0:
            await self.rotate_to_next_wifi_profile()
        else:
            log.info(f"In profile {self.current_profile.ssid.value} for another {self.time_until_next_profile:.1f} seconds")

        # Publish the SSID we're actually connected to so co-located meter-reader
        # apps (endress-promag) can poll only while their own AP is active. The
        # E+H meter web server is single-session, so concurrent readers starve
        # each other.
        await self.tags.current_ssid.set(self.connected_ssid)

    async def rotate_to_next_wifi_profile(self, increment=True):
        log.info(f"Rotating to next wifi profile {self.next_profile.ssid.value}")
        if increment:
            self.current_profile_index += 1
            if self.current_profile_index >= len(self.profiles):
                self.current_profile_index = 0
        self.last_wifi_change = time.time()
        ssid = self.current_profile.ssid.value
        try:
            # Activate the pre-provisioned NetworkManager profile rather than
            # `device wifi connect`. The doovit host's NetworkManager is older
            # than the container's nmcli, and `wifi_connect` rewrites the whole
            # profile — tripping `connection.autoconnect-ports: unknown property`
            # across that version skew. `connection up` only activates an existing
            # profile and is skew-tolerant (it's what the doovit's own wifi
            # manager uses). Requires the profile to already exist on the host.
            nmcli.connection.up(ssid)
            self.connected_ssid = ssid
        except Exception as e:
            log.error(f"Error activating profile {ssid}, attempting direct connect: {e}")
            try:
                nmcli.device.wifi_connect(ssid, self.current_profile.password.value)
                self.connected_ssid = ssid
            except Exception as e2:
                log.error(f"Error connecting to {ssid}: {e2}")

    @property
    def profiles(self):
        return self.config.profiles.elements

    @property
    def time_in_current_profile(self):
        return time.time() - self.last_wifi_change

    @property
    def time_until_next_profile(self):
        return self.current_profile.hold_time.value - self.time_in_current_profile

    @property
    def current_profile(self):
        if self.current_profile_index >= len(self.profiles):
            self.current_profile_index = 0
        return self.profiles[self.current_profile_index]

    @property
    def next_profile(self):
        next_index = self.current_profile_index + 1
        if next_index >= len(self.profiles):
            next_index = 0
        return self.profiles[next_index]