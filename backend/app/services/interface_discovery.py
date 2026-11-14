
from scapy.all import conf, get_if_addr, get_if_hwaddr, get_if_list


def discover_interfaces():
    """
    Discover real network interfaces using Scapy.
    """

    interfaces = []

    # Identify the interface used by the default IPv4 route
    try:
        default_route = conf.route.route("0.0.0.0")
        default_interface = default_route[1]
    except Exception:
        default_interface = None

    for interface in get_if_list():
        try:
            ip_address = get_if_addr(interface)
        except Exception:
            ip_address = None

        try:
            mac_address = get_if_hwaddr(interface)
        except Exception:
            mac_address = None

        has_ipv4 = bool(
            ip_address and ip_address != "0.0.0.0"
        )

        interfaces.append({
            "name": interface,
            "ip_address": ip_address if has_ipv4 else None,
            "mac_address": mac_address,
            "has_ipv4": has_ipv4,
            "is_default_route": (
                interface == default_interface
            ),
        })

    return {
        "interfaces": interfaces,
        "default_interface": default_interface,
        "total": len(interfaces),
    }
