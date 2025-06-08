def log_mac_entry(mac_address, signal_strength, timestamp):
    with open('mac_log.txt', 'a') as log_file:
        log_file.write(f"{timestamp}: MAC Address: {mac_address}, Signal Strength: {signal_strength}\n")

def get_latest_mac_entries():
    mac_entries = {}
    try:
        with open('mac_log.txt', 'r') as log_file:
            for line in log_file:
                parts = line.strip().split(", ")
                timestamp = parts[0].split(": ")[0]
                mac_address = parts[1].split(": ")[1]
                signal_strength = parts[2].split(": ")[1]
                
                if mac_address not in mac_entries or mac_entries[mac_address]['timestamp'] < timestamp:
                    mac_entries[mac_address] = {
                        'signal_strength': signal_strength,
                        'timestamp': timestamp
                    }
    except FileNotFoundError:
        pass  # Log file does not exist yet
    return mac_entries