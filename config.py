import os
import socket

class Config:
    @staticmethod
    def find_available_port():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()
        return port

    @staticmethod
    def write_port_to_file(port):
        with open('server_port.txt', 'w') as f:
            f.write(str(port))

    @staticmethod
    def get_port_from_file():
        with open('server_port.txt', 'r') as f:
            return int(f.read().strip())

if __name__ == '__main__':
    port = Config.find_available_port()
    Config.write_port_to_file(port)
    print(f"Port {port} written to server_port.txt")
