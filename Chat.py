import socket
import threading

class Peer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.clients = []
        self.running = True

    def start_server(self):
        """Function to start the server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.ip}:{self.port}")

        while self.running:
            client_socket, addr = self.server_socket.accept()
            print(f"Connection from {addr}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        """Function to handle messages from clients"""
        try:
            while True:
                message = client_socket.recv(1024).decode()
                if not message or message == "EXIT":
                    print("Client disconnected")
                    self.clients.remove(client_socket)
                    client_socket.close()
                    break
                print(f"Received: {message}")
                self.broadcast(message, client_socket)
        except Exception as e:
            print(f"Error: {e}")
            self.clients.remove(client_socket)
            client_socket.close()

    def broadcast(self, message, sender_socket):
        """Function to broadcast message to other clients"""
        for client in self.clients:
            if client != sender_socket:
                client.send(f"Message from a peer: {message}".encode())

    def connect_to_peer(self, peer_ip, peer_port):
        """Function to connect as client to another peer"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((peer_ip, peer_port))
            print(f"Connected to peer {peer_ip}:{peer_port}")

            threading.Thread(target=self.send_messages).start()
            self.receive_messages()
        except Exception as e:
            print(f"Connection failed: {e}")

    def send_messages(self):
        """Function to send messages to the connected peer"""
        while True:
            message = input("You: ")
            if message == "EXIT":
                self.client_socket.send(message.encode())
                self.client_socket.close()
                break
            self.client_socket.send(message.encode())

    def receive_messages(self):
        """Function to receive messages from the connected peer"""
        try:
            while True:
                message = self.client_socket.recv(1024).decode()
                if not message:
                    break
                print(message)
        except Exception as e:
            print(f"Error: {e}")

    def stop(self):
        """Stop the server and close connections"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()


def start_as_server():
    """Function to start server mode"""
    peer = Peer("127.0.0.1", 5000)
    threading.Thread(target=peer.start_server).start()
    return peer


def start_as_client():
    """Function to start client mode"""
    peer = Peer("127.0.0.1", 5000)
    target_ip = input("Enter peer IP: ")
    target_port = int(input("Enter peer port: "))
    peer.connect_to_peer(target_ip, target_port)
    return peer


if __name__ == "__main__":
    print("1. Start as server")
    print("2. Connect as client")
    choice = input("Choose (1/2): ")

    if choice == "1":
        peer = start_as_server()
    elif choice == "2":
        peer = start_as_client()

    # Keep the main thread alive to handle server/client
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Shutting down...")
        peer.stop()
