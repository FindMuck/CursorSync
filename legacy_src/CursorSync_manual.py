import sys
import pyautogui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QLabel
from socket import socket, gethostbyname, gethostname, AF_INET, SOCK_STREAM
import threading

class CursorSyncApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.clients = []
        self.running = True
        self.server_socket = None
        self.client_socket = None
        self.connection_thread = None
        self.server_ip = self.get_server_ip()

    def initUI(self):
        self.setWindowTitle("Cursor Synchronizer")
        self.setGeometry(100, 100, 400, 200)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        self.master_ip_input = QLineEdit()
        self.master_ip_input.setPlaceholderText("Enter the IP address of the PC from which you will synchronize")
        self.master_ip_input.editingFinished.connect(self.start_client)
        self.x_input = QLineEdit()
        self.y_input = QLineEdit()
        main_layout.addWidget(QLabel("Master IP:"))
        main_layout.addWidget(self.master_ip_input)
        main_layout.addWidget(QLabel("X:"))
        main_layout.addWidget(self.x_input)
        main_layout.addWidget(QLabel("Y:"))
        main_layout.addWidget(self.y_input)

        self.go_button = QPushButton("Go!")
        self.go_button.clicked.connect(self.move_cursor)
        main_layout.addWidget(self.go_button)

        self.setCentralWidget(main_widget)

    def get_server_ip(self):
        try:
            server_ip = gethostbyname(gethostname())
            return server_ip
        except Exception as e:
            print("Failed to get server IP:", e)
            return None

    def move_cursor(self):
        try:
            x = int(self.x_input.text())
            y = int(self.y_input.text())
            pyautogui.moveTo(x, y)
            pyautogui.click(x, y)
            self.send_to_clients(f"{x},{y}")
        except ValueError:
            print("Invalid X or Y value.")

    def send_to_clients(self, coordinates):
        for client in self.clients:
            try:
                client.send(coordinates.encode())
            except Exception as e:
                print(f"Failed to send coordinates to client: {e}")
                client.close()
                self.clients.remove(client)

    def start_server(self):
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', 666))
        self.server_socket.listen(5)

        while self.running:
            client_socket, addr = self.server_socket.accept()
            print(f"Connection from {addr} has been established.")
            self.clients.append(client_socket)

    def start_client(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None

        master_ip = self.master_ip_input.text()
        if master_ip != self.server_ip:
            if self.connection_thread and self.connection_thread.is_alive():
                self.running = False
                self.connection_thread.join()
                self.running = True
            self.connection_thread = threading.Thread(target=self.attempt_connection, args=(master_ip,), daemon=True)
            self.connection_thread.start()

    def attempt_connection(self, master_ip):
        last_error = None
        while self.running:
            try:
                if self.client_socket:
                    self.client_socket.close()
                self.client_socket = socket(AF_INET, SOCK_STREAM)
                self.client_socket.settimeout(1)
                self.client_socket.connect((master_ip, 666))
                self.client_socket.settimeout(None)
                self.receive_from_server()
                last_error = None
            except Exception as e:
                if master_ip.count('.') == 3 and str(e) != last_error:
                    print(f"Failed to connect to {master_ip}: {e}")
                    last_error = str(e)

    def receive_from_server(self):
        while self.running and self.client_socket:
            try:
                coordinates = self.client_socket.recv(1024).decode()
                x, y = map(int, coordinates.split(','))
                pyautogui.moveTo(x, y)
                pyautogui.click(x, y)
            except Exception as e:
                print(f"Failed to receive coordinates: {e}")

    def closeEvent(self, event):
        self.running = False
        if self.server_socket:
            for client in self.clients:
                client.close()
        if self.client_socket:
            self.client_socket.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    cursor_sync_app = CursorSyncApp()
    cursor_sync_app.show()

    server_thread = threading.Thread(target=cursor_sync_app.start_server)
    server_thread.daemon = True
    server_thread.start()

    sys.exit(app.exec_())
