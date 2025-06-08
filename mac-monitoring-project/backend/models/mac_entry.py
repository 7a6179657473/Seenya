class MacEntry:
    def __init__(self, mac_address, signal_strength, last_seen):
        self.mac_address = mac_address
        self.signal_strength = signal_strength
        self.last_seen = last_seen

    def __repr__(self):
        return f"MacEntry(mac_address={self.mac_address}, signal_strength={self.signal_strength}, last_seen={self.last_seen})"