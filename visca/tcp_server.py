"""TCP server for VISCA communication.

Handles VISCA protocol communication over TCP, proxying data between
TCP clients and the serial port connected to the camera.
"""

from select import select
import socket
import time
from typing import Optional

from visca.config import VISCA_IP_HOST, VISCA_IP_PORT
from visca.logging import log
from visca.serial_bridge import read_serial_response, serial_conn


# Global state variables
visca_socket: Optional[socket.socket] = None
clients: list = []
running: bool = False

stats = {
    'start_time': int(time.time()),
    'clients': 0,
    'total_conn': 0,
    'ip_to_rs232': 0,
    'rs232_to_ip': 0,
    'last_activity': 0
}


def setup_visca_server() -> bool:
    """Create, bind and listen on the VISCA TCP server socket.

    Returns True on success, False on failure. Binds to VISCA_IP_HOST:VISCA_IP_PORT.
    """
    global visca_socket
    try:
        visca_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        visca_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Try to set SO_REUSEPORT for quick restarts across processes. On
        # some platforms (older kernels, restricted containers) this may
        # raise; that's acceptable — the exception is caught below and
        # logged from the caller.
        try:
            visca_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except Exception:
            # Not fatal; continue without SO_REUSEPORT.
            pass

        visca_socket.setblocking(0)

        # Wait a bit in case port is still in TIME_WAIT
        time.sleep(1)

        visca_socket.bind((VISCA_IP_HOST, VISCA_IP_PORT))
        visca_socket.listen(5)
        log('I', f'VISCA: {VISCA_IP_HOST}:{VISCA_IP_PORT}')
        return True
    except Exception as e:
        log('E', f'VISCA error: {e}')
        log('E', f'Try checking port with: sudo lsof -i :{VISCA_IP_PORT}')
        return False


def handle_visca() -> None:
    """Accept new TCP clients and proxy data between TCP clients and serial.

    Called repeatedly from visca_loop(). Uses select() with a short timeout to
    avoid blocking the background thread.
    """
    global clients, stats

    if not visca_socket:
        return

    # Build the readable list for select(): the listening socket plus any
    # currently connected client sockets. Sockets are non-blocking.
    readable = [visca_socket] + clients

    try:
        ready, _, _ = select(readable, [], [], 0.01)
    except Exception as e:
        log('W', f'Select error: {e}')
        return

    for sock in ready:
        if sock is visca_socket:
            # New connection on the listening socket
            try:
                client, addr = visca_socket.accept()
                client.setblocking(0)
                clients.append(client)
                stats['clients'] = len(clients)
                stats['total_conn'] += 1
                log('I', f'Client connected: {addr[0]}:{addr[1]}')
            except Exception as e:
                log('W', f'Accept error: {e}')
        else:
            # Data from a client socket
            try:
                data = sock.recv(1024)
                if data:
                    # Forward to serial
                    if serial_conn and serial_conn.is_open:
                        try:
                            serial_conn.write(data)
                            serial_conn.flush()
                            stats['ip_to_rs232'] += 1
                            stats['last_activity'] = int(time.time())
                            log('D', f'IP->RS232: {data.hex()}')

                            # Wait for a (synchronous) response from the
                            # camera. Many VISCA commands produce an
                            # immediate response; read_serial_response will
                            # return None on timeout.
                            response = read_serial_response()
                            if response:
                                try:
                                    sock.send(response)
                                    stats['rs232_to_ip'] += 1
                                    log('D', f'RS232->IP: {response.hex()}')
                                except Exception:
                                    pass
                        except Exception as e:
                            log('E', f'Serial write error: {e}')
                else:
                    # Client disconnected (recv returned empty bytes)
                    clients.remove(sock)
                    sock.close()
                    stats['clients'] = len(clients)
                    log('I', 'Client disconnected')
            except Exception as e:
                if sock in clients:
                    clients.remove(sock)
                    try:
                        sock.close()
                    except Exception:
                        pass
                    stats['clients'] = len(clients)


def visca_loop() -> None:
    """Background loop that handles socket IO and unsolicited serial data.

    Runs in a daemon thread; relies on the global `running` flag for shutdown.
    """
    global running, clients, stats
    log('I', 'VISCA Loop started')

    while running:
        try:
            handle_visca()

            # Unsolicited camera messages: if the camera sends bytes without
            # a preceding IP request, forward them to all connected clients.
            # This allows camera status messages to reach controllers.
            if serial_conn and serial_conn.is_open:
                try:
                    if serial_conn.in_waiting > 0:
                        data = serial_conn.read(serial_conn.in_waiting)
                        log('D', f'RS232 unsolicited: {data.hex()}')
                        for client in clients[:]:
                            try:
                                client.send(data)
                                stats['rs232_to_ip'] += 1
                            except Exception:
                                clients.remove(client)
                                try:
                                    client.close()
                                except Exception:
                                    pass
                except Exception:
                    pass

            time.sleep(0.01)
        except Exception as e:
            log('E', f'VISCA loop error: {e}')
            time.sleep(0.1)
