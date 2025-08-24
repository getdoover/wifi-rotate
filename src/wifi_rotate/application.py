import logging
import time
import nmcli
import traceback

from pydoover.docker import Application

from .app_config import WifiRotateConfig

log = logging.getLogger()

class WifiRotateApplication(Application):
    config: WifiRotateConfig  # not necessary, but helps your IDE provide autocomplete!

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.loop_target_period = 5 # seconds
        self.started: float = time.time()

        self.current_profile_index = 0
        self.last_wifi_change = time.time()

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

    async def rotate_to_next_wifi_profile(self, increment=True):
        log.info(f"Rotating to next wifi profile {self.next_profile.ssid.value}")
        if increment:
            self.current_profile_index += 1
            if self.current_profile_index >= len(self.profiles):
                self.current_profile_index = 0
        self.last_wifi_change = time.time()
        try:
            nmcli.device.wifi_connect(self.current_profile.ssid.value, self.current_profile.password.value)
        except Exception as e:
            log.error(f"Error connecting to {self.current_profile.ssid.value}: {e}")
            # traceback.print_exc()

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