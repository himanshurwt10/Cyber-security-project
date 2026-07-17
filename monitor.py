"""
Keeps track of devices and determines
whether they are Online, Offline, or New.
"""

from datetime import datetime


class NetworkMonitor:

    def __init__(self):
        # Stores all known devices
        self.devices = {}

    def update(self, scanned_devices):
        """
        scanned_devices:
        [
            {
                "ip": "...",
                "mac": "...",
                "hostname": "..."
            }
        ]
        """

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Current IPs found in this scan
        current_ips = set()

        for device in scanned_devices:

            ip = device["ip"]

            current_ips.add(ip)

            if ip not in self.devices:

                # New Device
                self.devices[ip] = {
                    "ip": ip,
                    "mac": device["mac"],
                    "vendor": device["vendor"],
                    "hostname": device["hostname"],
                    "status": "New",
                    "first_seen": current_time,
                    "last_seen": current_time
                }

            else:

                # Existing Device
                self.devices[ip]["mac"] = device["mac"]
                self.devices[ip]["vendor"] = device["vendor"]
                self.devices[ip]["hostname"] = device["hostname"]
                self.devices[ip]["status"] = "Online"
                self.devices[ip]["last_seen"] = current_time


        # Devices missing from this scan are Offline
        for ip in self.devices.keys():

            if ip not in current_ips:

                self.devices[ip]["status"] = "Offline"

        return self.get_devices()

    def get_devices(self):
        """
        Returns all devices sorted by IP.
        """

        return sorted(
            self.devices.values(),
            key=lambda x: list(map(int, x["ip"].split(".")))
        )

    def online_count(self):

        return sum(
            1
            for device in self.devices.values()
            if device["status"] in ("Online", "New")
        )

    def offline_count(self):

        return sum(
            1
            for device in self.devices.values()
            if device["status"] == "Offline"
        )

    def total_devices(self):

        return len(self.devices)