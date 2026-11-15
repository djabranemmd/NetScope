
import threading

from collections import deque

from scapy.all import AsyncSniffer, get_if_addr, get_if_list

from app.services.packet_parser import parse_packet


class PacketCaptureEngine:
    """
    Real-time network packet capture engine.

    Captures IPv4 packets and stores metadata only.
    """

    def __init__(self, max_packets=500):
        self.sniffer = None

        self.is_running = False
        self.interface = None
        self.local_ip = None

        self.lock = threading.RLock()

        self.packets = deque(maxlen=max_packets)

        self.stats = {
            "total_packets": 0,
            "total_bytes": 0,

            "incoming_packets": 0,
            "incoming_bytes": 0,

            "outgoing_packets": 0,
            "outgoing_bytes": 0,

            "unknown_direction_packets": 0,
            "unknown_direction_bytes": 0,

            "protocols": {},
        }

        self.last_error = None

    def _process_packet(self, packet):
        """Process every packet captured by Scapy."""

        try:
            parsed_packet = parse_packet(
                packet,
                local_ip=self.local_ip,
            )

            if parsed_packet is None:
                return

            with self.lock:
                self.packets.append(parsed_packet)

                packet_size = parsed_packet["packet_size"]

                self.stats["total_packets"] += 1
                self.stats["total_bytes"] += packet_size

                direction = parsed_packet["direction"]

                if direction == "INCOMING":
                    self.stats["incoming_packets"] += 1
                    self.stats["incoming_bytes"] += packet_size

                elif direction == "OUTGOING":
                    self.stats["outgoing_packets"] += 1
                    self.stats["outgoing_bytes"] += packet_size

                else:
                    self.stats["unknown_direction_packets"] += 1
                    self.stats["unknown_direction_bytes"] += packet_size

                protocol = parsed_packet["protocol"]

                self.stats["protocols"][protocol] = (
                    self.stats["protocols"].get(protocol, 0) + 1
                )

        except Exception as error:
            with self.lock:
                self.last_error = str(error)

    def start(self, interface):
        """Start packet capture on a selected interface."""

        with self.lock:
            if self.is_running:
                raise RuntimeError(
                    "Packet capture is already running."
                )

            if interface not in get_if_list():
                raise ValueError(
                    f"Interface '{interface}' does not exist."
                )

            local_ip = get_if_addr(interface)

            if not local_ip or local_ip == "0.0.0.0":
                raise ValueError(
                    "Selected interface has no valid IPv4 address."
                )

            self.interface = interface
            self.local_ip = local_ip
            self.last_error = None

            try:
                self.sniffer = AsyncSniffer(
                    iface=interface,
                    prn=self._process_packet,
                    store=False,
                    filter="ip",
                )

                self.sniffer.start()
                self.is_running = True

            except Exception as error:
                self.sniffer = None
                self.is_running = False
                self.interface = None
                self.local_ip = None
                self.last_error = str(error)

                raise RuntimeError(
                    f"Failed to start packet capture: {error}"
                ) from error

            return self.get_status()

    def stop(self):
        """Stop capture without holding the lock during thread join."""

        with self.lock:
            if not self.is_running:
                return self.get_status()

            sniffer = self.sniffer

        try:
            if sniffer and sniffer.running:
                sniffer.stop(join=True)

        except Exception as error:
            with self.lock:
                self.last_error = str(error)

            raise RuntimeError(
                f"Failed to stop packet capture: {error}"
            ) from error

        finally:
            with self.lock:
                self.is_running = False
                self.sniffer = None

        return self.get_status()

    def get_status(self):
        """Return current capture status and statistics."""

        with self.lock:
            return {
                "is_running": self.is_running,
                "interface": self.interface,
                "local_ip": self.local_ip,

                "stats": {
                    **self.stats,
                    "protocols": dict(self.stats["protocols"]),
                },

                "buffered_packets": len(self.packets),
                "last_error": self.last_error,
            }

    def get_packets(self, limit=100):
        """Return the latest captured packet metadata."""

        with self.lock:
            return list(self.packets)[-limit:]


capture_engine = PacketCaptureEngine()
