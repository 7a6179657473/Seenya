from flask import Blueprint, request, jsonify
from ..models.mac_entry import MacEntry
from ..utils.logger import log_mac_entry

mac_routes = Blueprint('mac_routes', __name__)

mac_entries = {}

@mac_routes.route('/log_mac', methods=['POST'])
def log_mac():
    data = request.json
    mac_address = data.get('mac_address')
    signal_strength = data.get('signal_strength')

    if not mac_address or not signal_strength:
        return jsonify({'error': 'MAC address and signal strength are required'}), 400

    mac_entry = MacEntry(mac_address, signal_strength)
    mac_entries[mac_address] = mac_entry
    log_mac_entry(mac_entry)

    return jsonify({'message': 'MAC address logged successfully', 'last_seen': mac_entry.last_seen}), 201

@mac_routes.route('/mac_entries', methods=['GET'])
def get_mac_entries():
    return jsonify([entry.to_dict() for entry in mac_entries.values()]), 200