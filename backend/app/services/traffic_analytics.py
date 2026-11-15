
from collections import defaultdict
from datetime import datetime, timezone

from app.services.packet_capture import capture_engine


def get_traffic_analytics(window_seconds=10, top_limit=5):
    """
    Calculate traffic analytics from real captured packet metadata.

    Analytics are calculated using the packets currently retained
    in the capture engine's buffer.

    No packet payload is stored or analyzed.
    """

    now = datetime.now(timezone.utc)

    capture_status = capture_engine.get_status()
    packets = capture_engine.get_packets(limit=500)

    # Keep only packets captured within the requested time window.
    recent_packets = []

    for packet in packets:
        try:
            timestamp = datetime.fromisoformat(
                packet["timestamp"]
            )

            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(
                    tzinfo=timezone.utc
                )

            age = (now - timestamp).total_seconds()

            if 0 <= age <= window_seconds:
                recent_packets.append(packet)

        except (KeyError, TypeError, ValueError):
            continue

    # Initialize analytics counters.
    total_packets = len(recent_packets)
    total_bytes = 0

    incoming_bytes = 0
    outgoing_bytes = 0
    unknown_bytes = 0

    incoming_packets = 0
    outgoing_packets = 0
    unknown_packets = 0

    protocol_stats = defaultdict(
        lambda: {
            "packets": 0,
            "bytes": 0,
        }
    )

    source_stats = defaultdict(
        lambda: {
            "packets": 0,
            "bytes": 0,
        }
    )

    destination_stats = defaultdict(
        lambda: {
            "packets": 0,
            "bytes": 0,
        }
    )

    # Process real packet metadata.
    for packet in recent_packets:
        packet_size = int(packet.get("packet_size", 0))
        protocol = packet.get("protocol", "OTHER")

        source_ip = packet.get("source_ip")
        destination_ip = packet.get("destination_ip")

        direction = packet.get("direction", "UNKNOWN")

        total_bytes += packet_size

        # Direction statistics.
        if direction == "INCOMING":
            incoming_packets += 1
            incoming_bytes += packet_size

        elif direction == "OUTGOING":
            outgoing_packets += 1
            outgoing_bytes += packet_size

        else:
            unknown_packets += 1
            unknown_bytes += packet_size

        # Protocol statistics.
        protocol_stats[protocol]["packets"] += 1
        protocol_stats[protocol]["bytes"] += packet_size

        # Source IP statistics.
        if source_ip:
            source_stats[source_ip]["packets"] += 1
            source_stats[source_ip]["bytes"] += packet_size

        # Destination IP statistics.
        if destination_ip:
            destination_stats[destination_ip]["packets"] += 1
            destination_stats[destination_ip]["bytes"] += packet_size

    # Calculate average bandwidth over the complete window.
    bytes_per_second = total_bytes / window_seconds

    incoming_bps = (
        incoming_bytes * 8
    ) / window_seconds

    outgoing_bps = (
        outgoing_bytes * 8
    ) / window_seconds

    total_bps = bytes_per_second * 8

    # Sort IP statistics by transferred bytes.
    top_sources = sorted(
        [
            {
                "ip_address": ip,
                **stats,
            }
            for ip, stats in source_stats.items()
        ],
        key=lambda item: item["bytes"],
        reverse=True,
    )[:top_limit]

    top_destinations = sorted(
        [
            {
                "ip_address": ip,
                **stats,
            }
            for ip, stats in destination_stats.items()
        ],
        key=lambda item: item["bytes"],
        reverse=True,
    )[:top_limit]

    # Sort protocol statistics by packet count.
    protocols = [
        {
            "protocol": protocol,
            **stats,
        }
        for protocol, stats in protocol_stats.items()
    ]

    protocols.sort(
        key=lambda item: item["packets"],
        reverse=True,
    )

    return {
        "capture": {
            "is_running": capture_status["is_running"],
            "interface": capture_status["interface"],
            "local_ip": capture_status["local_ip"],
        },

        "measurement": {
            "window_seconds": window_seconds,
            "buffered_packets": len(packets),
            "analyzed_packets": total_packets,
            "measurement_time": now.isoformat(),
        },

        "traffic": {
            "total_packets": total_packets,
            "total_bytes": total_bytes,
            "packets_per_second": round(
                total_packets / window_seconds,
                2,
            ),
        },

        "bandwidth": {
            "total_mbps": round(
                total_bps / 1_000_000,
                6,
            ),
            "incoming_mbps": round(
                incoming_bps / 1_000_000,
                6,
            ),
            "outgoing_mbps": round(
                outgoing_bps / 1_000_000,
                6,
            ),
        },

        "directions": {
            "incoming": {
                "packets": incoming_packets,
                "bytes": incoming_bytes,
            },
            "outgoing": {
                "packets": outgoing_packets,
                "bytes": outgoing_bytes,
            },
            "unknown": {
                "packets": unknown_packets,
                "bytes": unknown_bytes,
            },
        },

        "protocols": protocols,

        "top_sources": top_sources,

        "top_destinations": top_destinations,
    }
