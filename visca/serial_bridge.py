"""Serial port bridge for VISCA communication.

Handles opening, reading from, and writing to the serial port
that connects to the VISCA camera.
"""

from time import time, sleep
from typing import Optional
import serial

from visca.config import (
    choose_serial_port,
    SERIAL_PORT,
    SERIAL_BAUDRATE,
    SERIAL_TIMEOUT,
    RESPONSE_WAIT,
)
from visca.logging import log


# Global serial connection object
serial_conn: Optional[serial.Serial] = None


def setup_serial() -> bool:
    """Open and configure the serial port.

    Returns True on success, False on failure. Uses choose_serial_port() to
    select the device and creates a pyserial Serial object assigned to the
    module-level `serial_conn` variable.
    """
    global serial_conn
    port_to_use = choose_serial_port(SERIAL_PORT)

    try:
        serial_conn = serial.Serial(
            port=port_to_use,
            baudrate=SERIAL_BAUDRATE,
            timeout=SERIAL_TIMEOUT,
            write_timeout=SERIAL_TIMEOUT,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        # Clear buffers
        serial_conn.reset_input_buffer()
        serial_conn.reset_output_buffer()
        log('I', f'Serial: {port_to_use}@{SERIAL_BAUDRATE}')
        return True
    except Exception as e:
        log('E', f'Serial error: {e}')
        return False


def read_serial_response(timeout: float = RESPONSE_WAIT) -> Optional[bytes]:
    """Read a response from the serial device up to `timeout` seconds.

    VISCA messages are terminated with 0xFF. The loop reads available
    bytes and stops early when a trailing 0xFF is observed.

    Args:
        timeout: Maximum seconds to wait for a response

    Returns:
        bytes: Response data, or None if no response received or timeout
    """
    if not serial_conn or not serial_conn.is_open:
        return None

    start = time()
    response = b''

    while (time() - start) < timeout:
        try:
            if serial_conn.in_waiting > 0:
                chunk = serial_conn.read(serial_conn.in_waiting)
                response += chunk
                # VISCA response frames end with 0xFF; stop reading when
                # we see a chunk whose last byte is 0xFF.
                if chunk and chunk[-1] == 0xFF:
                    break
            sleep(0.01)
        except Exception as e:
            log('W', f'Serial read error: {e}')
            break

    return response if response else None


def send_command(hex_str: str) -> dict:
    """Send a VISCA hex command over the serial link and wait for a response.

    Args:
        hex_str: Hex string representation of VISCA command (spaces allowed)

    Returns:
        dict: Result dict with keys:
            - ok (bool): True if command sent successfully
            - len (int): Number of bytes sent
            - resp (str): Hex string of response, or None if no response
            On error: {'ok': False, 'err': '<message>'}
    """
    try:
        # Convert hex string to bytes
        data = bytes.fromhex(hex_str.replace(' ', ''))

        if not serial_conn or not serial_conn.is_open:
            return {'ok': False, 'err': 'Serial port not ready'}

        # Send command
        serial_conn.write(data)
        serial_conn.flush()
        log('I', f'CMD sent: {hex_str}')

        # Wait for response
        response = read_serial_response()

        result = {
            'ok': True,
            'len': len(data),
            'resp': response.hex() if response else None
        }

        if response:
            log('I', f'CMD response: {response.hex()}')
        else:
            log('W', 'No response from camera')

        return result

    except Exception as e:
        log('E', f'CMD Error: {str(e)}')
        return {'ok': False, 'err': str(e)}
