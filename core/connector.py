import qt_core as qt
import socket
from core.logger import Logger


class ProxyListener(qt.QObject):
    def __init__(self, connector, proxy_host):
        super().__init__()
        self.connector = connector
        self.proxy_host = proxy_host

    @qt.Slot()
    def listen_proxy(self):
        proxy = self.connector.proxies.get(self.proxy_host)
        if not proxy:
            self.connector.logger.warning(f"Proxy on {self.proxy_host} not found")
            return

        try:
            while proxy['running']:
                data = proxy['socket'].recv(4096)
                if not data:
                    break
                decoded = data.decode(errors="ignore").strip()
                for line in decoded.splitlines():
                    # noinspection PyTypeChecker
                    qt.QMetaObject.invokeMethod(
                        self.connector,
                        "_parse_message",
                        qt.Qt.ConnectionType.AutoConnection,
                        qt.Q_ARG(str, line),
                        qt.Q_ARG(str, self.proxy_host),
                    )
        except Exception as e:
            self.connector.logger.error(f"Failed to listen proxy on {self.proxy_host}: {e}")
        finally:
            # noinspection PyTypeChecker
            qt.QMetaObject.invokeMethod(
                self.connector,
                "disconnect_proxy",
                qt.Qt.ConnectionType.AutoConnection,
                qt.Q_ARG(str, self.proxy_host),
                qt.Q_ARG(bool, False)
            )


class Connector(qt.QObject):
    """
    proxies = {
        "host": {
            "socket": socket,
            "listener_thread": QThread,
            "worker": ProxyListener,
            "running": bool,
        }
    }

    "connections" = {
        conn_id: {
            "data": [
                "messages"
            ],
            "host": ip,
            "port": port,
            "status": status,
            "target": target_ip
        },
    }
    """
    connected = qt.Signal(str)
    disconnected = qt.Signal(str)
    message_received = qt.Signal(str)

    # sinais estruturados:
    connection_list = qt.Signal(str, str, int, str, str)
    port_added = qt.Signal(str, str, int, str)
    port_removed = qt.Signal(str)
    target_connected = qt.Signal(str, str, str)
    target_disconnected = qt.Signal(str, str)

    def __init__(self):
        super().__init__()
        self.logger = Logger(name="connector", level="DEBUG").get_logger()

        self.proxies = {}
        self.connections = {}

    def get_connection(self, conn_id: str) -> None | dict:
        connection = self.connections.get(conn_id, None)
        return connection

    def connect_proxy(self, proxy_host: str, proxy_port: int):
        if proxy_host in self.proxies.keys():
            self.logger.warning(f"Proxy {proxy_host} alredy connected")
            return

        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((proxy_host, proxy_port))

            listener_thread = qt.QThread(self)
            worker = ProxyListener(self, proxy_host)
            worker.moveToThread(listener_thread)

            listener_thread.started.connect(worker.listen_proxy)

            running = True

            self.proxies[proxy_host] = {
                "socket": conn,
                "listener_thread": listener_thread,
                "worker": worker,
                "running": running,
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
                proxy["listener_thread"].quit()
                proxy["listener_thread"].wait()
                proxy["worker"].deleteLater()
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

    def cleanup(self):
        self.logger.info("Starting connector cleanup...")
        proxy_hosts = list(self.proxies.keys())

        for proxy_host in proxy_hosts:
            proxy = self.proxies.get(proxy_host)
            if proxy:
                proxy["running"] = False
                try:
                    proxy["socket"].close()
                except Exception as e:
                    self.logger.warning(f"Failed to close socket: {e}")

        for proxy_host in proxy_hosts:
            proxy = self.proxies.get(proxy_host)
            if proxy:
                self.logger.debug(f"Cleaning up proxy {proxy_host}")
                try:
                    proxy["listener_thread"].quit()
                    if not proxy["listener_thread"].wait(2000):
                        self.logger.warning(f"Force terminating thread for {proxy_host}")
                        proxy["listener_thread"].terminate()
                        proxy["listener_thread"].wait(1000)

                    proxy["worker"].deleteLater()

                except Exception as e:
                    self.logger.error(f"Error cleaning proxy {proxy_host}: {e}")

        self.proxies.clear()
        self.connections.clear()
        self.logger.info("Connector cleanup completed")

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
    # Parser Proxy
    # =============================

    @qt.Slot(str, str)
    def _parse_message(self, message: str, proxy_host: str):
        self.logger.debug(f"Parsing message from [{proxy_host}]: {message}")
        if message.startswith("[PORT_ADDED]"):
            parts = message.split()
            if len(parts) != 5:
                return
            _, conn_id, host, port, status = parts
            self.port_added.emit(conn_id, host, int(port), status)

        elif message.startswith("[PORT_REMOVED]"):
            parts = message.split()
            if len(parts) != 2:
                return
            _, conn_id = parts
            self.port_removed.emit(conn_id)

        elif message.startswith("[TARGET_CONNECTED]"):
            parts = message.split()
            if len(parts) != 4:
                return
            _, conn_id, ip, status = parts
            self.target_connected.emit(conn_id, ip, status)

        elif message.startswith("[TARGET_DISCONNECTED]"):
            parts = message.split()
            if len(parts) != 3:
                return
            _, conn_id, status = parts
            self.target_disconnected.emit(conn_id, status)

        elif message.startswith("[CONNECTION]"):
            parts = message.split()
            if len(parts) != 6:
                return
            _, conn_id, host, port, status, target = parts
            self.connection_list.emit(conn_id, host, int(port), status, target)

        else:
            self.message_received.emit(message)
