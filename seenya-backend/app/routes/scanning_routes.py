"""
API Routes for Wireless Scanning Operations
"""

from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from services.wireless_scanner import scanner


scanning_bp = Blueprint('scanning', __name__, url_prefix='/api/scanning')


@scanning_bp.route('/interfaces', methods=['GET'])
def get_wireless_interfaces():
    """
    Get available wireless network interfaces
    """
    try:
        interfaces = scanner.get_wireless_interfaces()
        return jsonify({
            'success': True,
            'interfaces': interfaces
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@scanning_bp.route('/start', methods=['POST'])
def start_scanning():
    """
    Start wireless scanning
    """
    try:
        data = request.get_json() or {}
        interface = data.get('interface')
        
        if scanner.is_scanning:
            return jsonify({
                'success': False,
                'error': 'Scanning is already active'
            }), 400
        
        success = scanner.start_scanning(interface)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Wireless scanning started',
                'interface': interface or 'auto-detected'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start scanning'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@scanning_bp.route('/stop', methods=['POST'])
def stop_scanning():
    """
    Stop wireless scanning
    """
    try:
        scanner.stop_scanning()
        return jsonify({
            'success': True,
            'message': 'Wireless scanning stopped'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@scanning_bp.route('/status', methods=['GET'])
def get_scanning_status():
    """
    Get current scanning status
    """
    try:
        return jsonify({
            'success': True,
            'is_scanning': scanner.is_scanning,
            'devices_detected': len(scanner.detected_devices)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@scanning_bp.route('/devices', methods=['GET'])
def get_detected_devices():
    """
    Get all detected devices
    """
    try:
        devices = scanner.get_detected_devices()
        return jsonify({
            'success': True,
            'devices': devices,
            'count': len(devices)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@scanning_bp.route('/devices/clear', methods=['POST'])
def clear_detected_devices():
    """
    Clear all detected devices
    """
    try:
        scanner.clear_detected_devices()
        return jsonify({
            'success': True,
            'message': 'Detected devices cleared'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
