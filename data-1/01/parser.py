"""
BROWAN TBMS100 Motion Sensor Payload Decoder
Decodes payloads from TBMS100-915/868 LoRaWAN motion sensors.

Input formats supported:
- Hex string: "0109380A005A3D00" or "0x0109380A005A3D00"
- Binary string: b"\x01\x09\x38\x0A\x00\x5A\x3D\x00"
"""

import sys
import json
import argparse
from typing import Union, Tuple

def normalize(payload: Union[str, bytes]) -> bytes:
    """Convert various input formats to bytes."""
    if isinstance(payload, bytes):
        return payload
    
    try:
        hex_str = payload.lower().replace('0x', '')
        return bytes.fromhex(hex_str)
    except ValueError as e:
        raise ValueError(f"Invalid hex string: {payload}") from e

def parse(payload: bytes) -> Tuple[str, float, int, int, int]:
    """
    Parse payload bytes and return decoded values.
    
    Args:
        payload: 8 bytes of sensor data
        
    Returns:
        Tuple of (status, battery_voltage, temperature, time, count)
    """
    if len(payload) != 8:
        raise ValueError(f"Invalid payload length: {len(payload)} bytes (expected 8)")
    
    # Status (byte 0, bit 0)
    status = "occupied" if payload[0] & 0x01 else "free"
    
    # Battery (byte 1, bits 0-3)
    battery_value = payload[1] & 0x0F
    if not 1 <= battery_value <= 14:
        raise ValueError(f"Battery value {battery_value} out of range [1-14]")
    battery_voltage = (25 + battery_value) / 10
    
    # Temperature (byte 2, bits 0-6)
    temp_value = payload[2] & 0x7F
    temperature = temp_value - 32
    if not -32 <= temperature <= 95:
        raise ValueError(f"Temperature {temperature}°C out of range [-32-95]")
    
    # Time (bytes 3-4, little-endian)
    time = int.from_bytes(payload[3:5], byteorder='little', signed=False)
    
    # Count (bytes 5-7, little-endian)
    count = int.from_bytes(payload[5:8], byteorder='little', signed=False)
    
    return (status, battery_voltage, temperature, time, count)

def format_json(values: Tuple[str, float, int, int, int]) -> str:
    """Format decoded values as JSON string."""
    result = {
        "status": values[0],
        "battery": values[1],
        "temperature": values[2],
        "time": values[3],
        "count": values[4]
    }
    return json.dumps(result, indent=2)

def format_csv(values: Tuple[str, float, int, int, int]) -> str:
    """Format decoded values as CSV string."""
    headers = ['status', 'battery', 'temperature', 'time', 'count']
    values_str = [str(v) for v in values]
    return f"{','.join(headers)}\n{','.join(values_str)}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Decode BROWAN TBMS100 Motion Sensor payloads'
    )
    parser.add_argument('payload', help='Payload to decode (hex string)')
    parser.add_argument(
        '--format', 
        choices=['csv', 'json'], 
        default='json',
        help='Output format (default: json)'
    )
    args = parser.parse_args()

    try:
        # Normalize input and parse payload
        bytes_payload = normalize(args.payload)
        values = parse(bytes_payload)
        
        # Output in requested format
        if args.format == 'json':
            print(format_json(values))
        else:  # csv
            print(format_csv(values))
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)