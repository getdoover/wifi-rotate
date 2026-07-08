from pydoover.tags import Tag, Tags


class WifiRotateTags(Tags):
    # The SSID the device is currently connected to. Published so co-located
    # apps that read a per-AP device (e.g. the endress-promag meter apps) can
    # poll only while their own AP is the active one. The E+H meter web server
    # is single-session, so multiple concurrent readers starve each other.
    current_ssid = Tag("string", default=None)
