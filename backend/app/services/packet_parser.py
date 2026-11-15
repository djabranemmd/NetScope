
from datetime import datetime, timezone

from scapy.all import IP, TCP, UDP, DNS, DNSQR


def parse_packet(packet, local_ip=None):
    """
    Extract useful metadata from a real captured IPv4 packet.

    Packet payload is never stored or returned.
    """

    if not packet.haslayer(IP):
        return None

    ip_layer = packet[IP]

    source_ip = ip_layer.src
    destination_ip = ip_layer.dst

    protocol = "OTHER"
    source_port = None
    destination_port = None

    if packet.haslayer(TCP):
        protocol = "TCP"
        source_port = packet[TCP].sport
        destination_port = packet[TCP].dport

    elif packet.haslayer(UDP):
        protocol = "UDP"
        source_port = packet[UDP].sport
        destination_port = packet[UDP].dport

    elif ip_layer.proto == 1:
        protocol = "ICMP"

    # Determine traffic direction relative to the selected interface
    if local_ip and source_ip == local_ip:
        direction = "OUTGOING"
    elif local_ip and destination_ip == local_ip:
        direction = "INCOMING"
    else:
        direction = "UNKNOWN"

    # Extract DNS query metadata without storing packet payload
    dns_query = None

    if packet.haslayer(DNS) and packet.haslayer(DNSQR):
        try:
            query = packet[DNSQR].qname

            if isinstance(query, bytes):
                dns_query = query.decode(
                    "utf-8",
                    errors="replace"
                ).rstrip(".")

        except (AttributeError, UnicodeError):
            dns_query = None

    return {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "source_ip": source_ip,
        "destination_ip": destination_ip,

        "source_port": source_port,
        "destination_port": destination_port,

        "protocol": protocol,
        "packet_size": len(packet),

        "direction": direction,
        "dns_query": dns_query,
    }
