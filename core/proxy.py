import socket
import threading
import secrets
import json
import os
from core.logger import Logger


class Proxy:
    def __init__(self, ip='0.0.0.0', port=8080):
        self.logger = Logger(name="proxy", level="DEBUG").get_logger()
        self.ip = ip
        self.port = port
        self.connections = {}

        self.server_conn = None
        self.controller_conn = None
        self.controller_addr = None
        self.controller_thread = None

        self.main_stop_event = threading.Event()

        self.main_stop_event.set()

    def start(self):
        self.main_stop_event.clear()
        self.controller_thread = threading.Thread(target=self._listen_controller, daemon=True)
        self.controller_thread.start()
        self.load_connections()
        self.logger.info(f"Proxy started on {self.ip}:{self.port}")

    def stop(self):
        if self.connections:
            self.save_connections()
        self.main_stop_event.set()
        try:
            if self.controller_conn:
                self.logger.info(f"Closing controller connection from {self.controller_addr}")
                self.controller_conn.close()

            if self.server_conn:
                self.logger.info("Closing main server socket")
                self.server_conn.close()

            if self.controller_thread:
                self.controller_thread.join()

            for conn_id, meta in self.connections.items():
                self.logger.info(f"Shutting down listener {conn_id}")
                if meta["socket"]:
                    meta["socket"].close()
                if meta["server"]:
                    meta["server"].close()
                if meta["event"]:
                    meta["event"].set()
                if meta["thread"]:
                    meta["thread"].join()
        except Exception as e:
            self.logger.error(f"Failed to stop proxy: {e}")
            return False

        self.logger.info("Proxy stoped")
        return True

    def status(self):
        msg = f"Running: {not self.main_stop_event.is_set()}"
        self.logger.info(msg)

    def show(self):
        description = f"Controller: {self.controller_addr}\n"

        total = len(self.connections)
        description += f"Total target connections: {total}\n"
        for conn_id, conn in self.connections.items():
            description += (
                f"-----------------------------\n"
                f"ID: {conn_id}\n"
                f"Address: {conn['addr']}\n"
                f"Status: {conn['Status']}\n"
                f"Data Length: {len(conn['data'])}\n"
            )
        self.logger.info(description)

    def save_connections(self):
        try:
            save_data = {}
            for conn_id, meta in self.connections.items():
                save_data[conn_id] = {
                    'addr': list(meta['addr']),
                    'status': meta['status'],
                    'data': meta['data']
                }

            with open("connections.json", "w") as f:
                json.dump(save_data, f, indent=4)

            self.logger.info(f"Saved connections to file connections.json")
        except Exception as e:
            self.logger.error(f'Failed to save connections: {e}')

    def load_connections(self):
        if not os.path.exists("connections.json"):
            return

        try:
            with open("connections.json", "r") as f:
                load_data = json.load(f)

            for conn_id, meta in load_data.items():
                host, port = meta['addr']
                data = meta['data']
                self._add_listener(host, port, conn_id_override=conn_id, data_messages=data)

            self.logger.info(f"Loaded connections from file connections.json")
        except Exception as e:
            self.logger.error(f'Failed to load connections: {e}')

    def _listen_controller(self):
        while not self.main_stop_event.is_set():
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.ip, self.port))
            server.listen(5)
            self.logger.info("Main server created")
            self.server_conn = server
            self._accept_controller(server)

    def _accept_controller(self, server):
        try:
            self.controller_conn, self.controller_addr = server.accept()
            self.logger.info(f"Controller connected from {self.controller_addr}")
            while not self.main_stop_event.is_set():
                try:
                    data = self.controller_conn.recv(1024)
                    if not data:
                        self.logger.warning("Controller connection closed")
                        break
                    self._process_command(data.decode(errors='ignore'))
                except Exception as e:
                    self.logger.warning(f"Controller disconnected: {e}")
                    break
        except Exception as e:
            self.logger.error(f"Failed to accept controller: {e}")
            return

    def _send_to_controller(self, msg: str):
        try:
            if self.controller_conn:
                self.logger.debug(msg)
                self.controller_conn.sendall(f"{msg}\n".encode(errors='ignore'))
        except Exception as e:
            self.logger.warning(e)

    def _add_listener(self, host, port, conn_id_override=None, data_messages=None):
        """
           connections = {
               conn_id: {
                   'server': target_conn_server_socket
                   'socket':  target_conn_socket,
                   'thread': target_thread,
                   'event': target_thread_event,
                   'data': [
                       'message1',
                       'message2'
                   ],
                   'addr': (ip, port),
                   'status': status
               }
           }
        """
        conn_id = conn_id_override or secrets.token_hex(7)
        stop_event = threading.Event()
        self.connections[conn_id] = {
            "server": None,
            "socket": None,
            "thread": None,
            "event": stop_event,
            "data": data_messages or [],
            "addr": (host, port),
            "target": "",
            "status": "Listening"
        }
        def accept_client(server):
            client = None
            try:
                client, addr = server.accept()
                self.connections[conn_id]["socket"] = client
                self.connections[conn_id]["status"] = "Connected"
                self.connections[conn_id]["target"] = addr[0]
                self._send_to_controller(f"[TARGET_CONNECTED] {conn_id} {addr[0]} Connected")
                self.logger.info(f"Target connected from {addr} (conn_id={conn_id})")
                while not (self.main_stop_event.is_set() or stop_event.is_set()):
                    try:
                        data = client.recv(4096)
                        if not data:
                            self.connections[conn_id]['status'] = "Disconnected"
                            self.connections[conn_id]['target'] = ""
                            self._send_to_controller(f"[TARGET_DISCONNECTED] {conn_id} Disconnected")
                            self.logger.warning(f"Target disconnected (conn_id={conn_id})")
                            break
                        self.connections[conn_id]['data'].append(data.decode(errors='ignore'))
                        self._send_to_controller(f"{conn_id} {data}")

                    except Exception as e:
                        self.logger.warning(f"Error receiving data from target {conn_id}: {e}")
                        break

            except Exception as e:
                self.logger.error(f"Listener accept failed (conn_id={conn_id}): {e}")
            finally:
                if client:
                    client.close()
                self.connections[conn_id]['status'] = "Listening"
                self.connections[conn_id]['target'] = ""
                self._send_to_controller(f"[TARGET_DISCONNECTED] {conn_id} Listening")
                self.logger.debug(f"Listening again (conn_id={conn_id})")

        def listen_client():
            while not (self.main_stop_event.is_set() or stop_event.is_set()):
                self.logger.info(f"Listener server created (conn_id={conn_id})")
                server_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_listener.bind((host, port))
                server_listener.listen(5)

                self.connections[conn_id]["server"] = server_listener
                accept_client(server_listener)

        thread_listener = threading.Thread(target=listen_client, daemon=True)
        self.connections[conn_id]["thread"] = thread_listener

        thread_listener.start()
        self._send_to_controller(f"[PORT_ADDED] {conn_id} {host} {port} Listening")
        self.logger.info(f"Listener added on {host}:{port} (conn_id={conn_id})")

    def _remove_listener(self, conn_id):
        conn = self.connections.get(conn_id)
        if not conn:
            self.logger.warning(f"Tried to remove non-existent connection: {conn_id}")
            return

        try:
            if conn["event"]:
                conn["event"].set()
            if conn["socket"]:
                conn["socket"].close()
            if conn["server"]:
                conn["server"].close()
            if conn["thread"]:
                conn["thread"].join()

            self._send_to_controller(f"[PORT_REMOVED] {conn_id}")
            self.logger.info(f"Listener removed (conn_id={conn_id})")
        except Exception as e:
            self.logger.error(f"Error removing listener {conn_id}: {e}")
        finally:
            del self.connections[conn_id]

    def _process_command(self, command):
        self.logger.debug(f"Processing command: {command}")

        if command.startswith("ADD_PORT"):
            parts = command.split()
            if len(parts) != 3:
                self.logger.warning("[x] Use: ADD_PORT <host> <port>")
                return
            _, host, port = parts
            self._add_listener(host, int(port))

        elif command.startswith("REMOVE_PORT"):
            _, listener_id = command.split()
            self._remove_listener(listener_id)

        elif command.startswith("LIST"):
            self.save_connections()
            for conn_id, meta in self.connections.items():
                host = meta['addr'][0]
                port = meta['addr'][1]
                status = meta['status']
                target = meta['target']
                self._send_to_controller(f"[CONNECTION] {conn_id} {host} {port} {status} ({target})")

    #     elif command.startswith("SEND"):
    #         _, conn_id, msg = command.split(" ", 2)
    #         if conn_id in self.targets:
    #             try:
    #                 self.targets[conn_id]['socket'].sendall(msg.encode())
    #             except:
    #                 self._send_to_controller(f"[x] Falha ao enviar para {conn_id}")
    #         else:
    #             self._send_to_controller(f"[x] Target {conn_id} não encontrado")

        else:
            self.logger.warning(f"Unknown command received: {command}")
    #
    #
    #     elif command.startswith("BROADCAST"):
    #         _, msg = command.split(" ", 1)
    #         for meta in self.targets.values():
    #             try:
    #                 meta['socket'].sendall(msg.encode())
    #             except:
    #                 pass
    #


if __name__ == '__main__':
    proxy = Proxy()
    try:
        while True:
            cmd = input("Proxy> ")
            if cmd == 'start':
                proxy.start()
            elif cmd == 'status':
                proxy.status()
            elif cmd == "stop":
                proxy.stop()
            elif cmd == "show":
                proxy.show()
            elif cmd == "exit":
                break
    except KeyboardInterrupt:
        proxy.stop()
        proxy.logger.critical("Abruptly stopped")
