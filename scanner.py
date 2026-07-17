"""
scanner.py
------------
Scans the local network using Scapy and returns
a list of active devices.

Author: Himanshu Rawat
"""

from scapy.all import ARP, Ether, srp
import socket
import ipaddress
from mac_vendor_lookup import MacLookup
# Change this if your subnet changes


def get_local_network():
    """
    Automatically detect the local IPv4 network.
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]

    finally:
        s.close()

    network = ipaddress.IPv4Network(
        ip + "/24",
        strict=False
    )

    return str(network)
NETWORK = get_local_network()
lookup = MacLookup()

try:
    lookup.update_vendors()
except Exception:
    pass


def get_hostname(ip):
    """
    Try to get the hostname of an IP address.
    Returns 'Unknown' if no hostname is found.
    """
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return hostname
    except Exception:
        return "Unknown"

def get_vendor(mac):
    """
    Returns the vendor/company name from a MAC address.
    """
    try:
        return lookup.lookup(mac)
    except Exception:
        return "Unknown"

def scan_network(network, timeout = 2):
    """
    Scan the network using ARP.

    Returns:
        list of dictionaries

        Example:
        [
            {
                "ip": "192.168.1.1",
                "mac": "AA:BB:CC:DD:EE:FF",
                "hostname": "Router"
            },
            ...
        ]
    """

    arp = ARP(pdst=network)

    ethernet = Ether(dst="ff:ff:ff:ff:ff:ff")

    packet = ethernet / arp

    answered = srp(
        packet,
        timeout=timeout,
        verbose=False
    )[0]

    devices = []

    for _, received in answered:

        device = {
            "ip": received.psrc,
            "mac": received.hwsrc,
            "vendor":get_vendor(received.hwsrc),
            "hostname": get_hostname(received.psrc)
        }

        devices.append(device)

    devices.sort(key=lambda x: list(map(int, x["ip"].split("."))))

    return devices


if __name__ == "__main__":

    print("Scanning network...\n")

    try:

        devices = scan_network(get_local_network())

        print("-" * 75)
        print(
            f"{'IP Address':<18}"
            f"{'MAC Address':<22}"
            f"{'Hostname'}"
        )
        print("-" * 75)

        for device in devices:

            print(
                f"{device['ip']:<18}"
                f"{device['mac']:<22}"
                f"{device['hostname']}"
            )

        print("-" * 75)
        print(f"\nTotal Devices Found: {len(devices)}")

    except PermissionError:

        print(
            "\nPermission denied.\n"
            "Run the program using sudo."
        )

    except Exception as e:

        print(f"\nError: {e}")