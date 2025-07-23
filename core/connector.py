import qt_core as qt
import socket
import threading
from core.logger import Logger


class Connector(qt.QObject):
    connected = qt.Signal(str)
    disconnected = qt.Signal(str)
    message_received = qt.Signal(str)

    # sinais estruturados:
    port_added = qt.Signal(str, str, int, str)
    port_removed = qt.Signal(str)
    target_connected = qt.Signal(str, str, str)
    target_disconnected = qt.Signal(str, str)
    connection_list = qt.Signal(list)

    def __init__(self):
        super().__init__()
        self.logger = Logger(name="connector", level="DEBUG").get_logger()

        """
        proxies = {
            "host": {
                "socket": socket,
                "listener_thread": Thread,
                "running": bool,
                "connections": {
                    conn_id: {
                        "data": [
                            "messages"
                        ],
                        "addr": (ip, port),
                        "status": status,
                    },                    
                }
            }
        }

        """
        self.proxies = {}

    def connect_proxy(self, proxy_host: str, proxy_port: int):
        if proxy_host in self.proxies.keys():
            self.logger.warning(f"Proxy {proxy_host} alredy connected")
            return

        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((proxy_host, proxy_port))

            listener_thread = threading.Thread(target=self._listen_proxy, args=(proxy_host,), daemon=True)

            running = True

            self.proxies[proxy_host] = {
                "socket": conn,
                "listener_thread": listener_thread,
                "running": running
            }

            listener_thread.start()
            self.connected.emit(proxy_host)
            self.logger.info(f"Connected to proxy on {proxy_host}:{proxy_port}")

        except Exception as e:
            self.logger.error(f"Error to connect proxy on {proxy_host}: {e}")
            self.disconnected.emit(proxy_host)

    def disconnect_proxy(self, proxy_host: str, join=True):
        proxy = self.proxies.get(proxy_host)
        if not proxy:
            self.logger.warning(f"Proxy on {proxy_host} not found")
            return

        proxy["running"] = False
        try:
            proxy["socket"].close()
            if join:
                proxy["listener_thread"].join()
        except Exception as e:
            self.logger.error(f"Error to close proxy on {proxy_host}: {e}")

        self.disconnected.emit(proxy_host)
        self.logger.debug(f"Proxy keys: {self.proxies.keys()}")
        if proxy_host in self.proxies.keys():
            del self.proxies[proxy_host]

    def send(self, proxy_host, command: str):
        proxy = self.proxies.get(proxy_host)
        if not proxy:
            self.logger.warning(f"Proxy on {proxy_host} not found")
            return

        try:
            conn = proxy['socket']
            conn.sendall((command.strip() + "\n").encode())
        except Exception as e:
            self.logger.error(f"Message to proxy on {proxy_host} failed: {e}")
            self.disconnected.emit()

    def _listen_proxy(self, proxy_host):
        proxy = self.proxies.get(proxy_host)
        if not proxy:
            self.logger.warning(f"Proxy on {proxy_host} not found")
            return

        try:
            while proxy['running']:
                data = proxy['socket'].recv(4096)
                if not data:
                    break
                decoded = data.decode(errors="ignore").strip()
                for line in decoded.splitlines():
                    self._parse_message(line)
        except Exception as e:
            self.logger.error(f"Failed to listen proxy on {proxy_host}: {e}")
        finally:
            self.disconnect_proxy(proxy_host, join=False)

    # =============================
    # Commands wrappers
    # =============================

    def send_add_port(self, host: str, port: int):
        self.send(host, f"ADD_PORT {host} {port}")

    def send_remove_port(self, host, conn_id: str):
        self.send(host, f"REMOVE_PORT {conn_id}")

    def send_list(self, host):
        self.send(host, "LIST")
    #
    # def send_broadcast(self, data: str):
    #     self.send(f"BROADCAST {data}")
    #
    # def send_to_target(self, target_id: str, data: str):
    #     self.send(f"SEND {target_id} {data}")

    # =============================
    # Parser das mensagens do proxy
    # =============================

    def _parse_message(self, message: str):
        if message.startswith("[PORT_ADDED]"):
            _, conn_id, host, port, status = message.split()
            self.port_added.emit(conn_id, host, int(port), status)

        elif message.startswith("[PORT_REMOVED]"):
            _, conn_id = message.split()
            self.port_removed.emit(conn_id)

        elif message.startswith("[TARGET_CONNECTED]"):
            _, conn_id, ip, status = message.split()
            self.target_connected.emit(conn_id, ip, status)

        elif message.startswith("[TARGET_DISCONNECTED]"):
            _, conn_id, status = message.split()
            self.target_disconnected.emit(conn_id, status)

        elif message.startswith("[CONNECTION]"):
            parts = message.split()
            if len(parts) != 5:
                return
            _, conn_id, host, port, status = parts
            info = {
                "id": conn_id,
                "host": host,
                "port": int(port),
                "status": status,
            }
            self.connection_list.emit([info])
        else:
            self.message_received.emit(message)
