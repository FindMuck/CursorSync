import os
import sys
import select
import time
import threading
from socket import socket, AF_INET, gethostbyname, gethostname, SOCK_DGRAM, SOCK_STREAM, SOL_SOCKET, SO_BROADCAST, timeout

import pyautogui
from PyQt5.QtCore import Qt, QEvent, QPoint
from PyQt5.QtGui import QIcon, QColor, QCursor, QPainter, QIntValidator, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QToolTip

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class CursorSync:
    def __init__(self, Sync_App):
        self.Sync_App = Sync_App

    def move_cursor(self):
        try:
            x = int(self.Sync_App.x_input.text())
            y = int(self.Sync_App.y_input.text())
            pyautogui.FAILSAFE = False
            pyautogui.moveTo(x, y)
            pyautogui.click(x, y)
            pyautogui.FAILSAFE = True
            self.Sync_App.network_operations.tcp_send_to_clients(f"GET_XY {x},{y}")
        except ValueError:
            print("Invalid X or Y value.", flush=True)

class NetworkOperations:
    def __init__(self, Sync_App):
        self.Sync_App = Sync_App
        self.servers_clients = []
        self.server_clients_sockets_list = []
        self.servers_clients_event = threading.Event()
        self.lock = threading.Lock()
        self.threads_list = {}

    @property
    def running(self):
        return self.Sync_App.running

    def broadcast_listener(self):
        try:
            udp_socket = socket(AF_INET, SOCK_DGRAM)
            udp_socket.bind(('', 666))

            host_ip = gethostbyname(gethostname())

            while self.running:
                data, ip = udp_socket.recvfrom(1024)
                if ip[0] != host_ip:
                    message = data.decode()
                    with self.lock:
                        if message == "START_SERVER" and ip[0] not in self.servers_clients:
                            self.servers_clients.append(ip[0])
                            self.servers_clients_event.set()
                            print("Received alive message:", message, "from", ip, flush=True)
                        elif message == "STOP_SERVER" and ip[0] in self.servers_clients:
                            self.servers_clients.remove(ip[0])
                            self.servers_clients_event.set()
                            print("Received stop message:", message, "from", ip, flush=True)
        finally:
            udp_socket.close()

    def broadcast_start_sender(self):
        try:
            udp_socket = socket(AF_INET, SOCK_DGRAM)
            udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

            message = "START_SERVER"

            while self.running:
                udp_socket.sendto(message.encode(), ('<broadcast>', 666))
                print("Broadcasted alive message to", '<broadcast>', flush=True)
                time.sleep(5)
        finally:
            udp_socket.close()

    def tcp_server_start(self):
        try:
            tcp_socket = socket(AF_INET, SOCK_STREAM)
            tcp_socket.bind(('0.0.0.0', 666))
            tcp_socket.listen(5)

            while self.running:
                ready, _, _ = select.select([tcp_socket], [], [])
                if self.running and ready:
                    client_socket, ip = tcp_socket.accept()
                    with self.lock:
                        self.server_clients_sockets_list.append(client_socket)
                    print(f"Connection from {ip} has been established.", flush=True)
        finally:
            tcp_socket.close()

    def tcp_clients_start(self):
        while self.running:
            self.servers_clients_event.wait()
            self.servers_clients_event.clear()
            if self.servers_clients:
                for ip in self.servers_clients:
                    if ip not in self.threads_list:
                        self.threads_list[ip] = threading.Thread(target=self.tcp_client_listener, args=(ip,), name=f'tcp_client_listener {ip}')
                        self.threads_list[ip].start()

    def tcp_client_listener(self, ip):
        def close_cleanup():
            tcp_socket.close()
            with self.lock:
                if ip in self.threads_list:
                    del self.threads_list[ip]
                    if ip in self.servers_clients:
                        self.servers_clients.remove(ip)
                        self.servers_clients_event.set()

        try:
            tcp_socket = socket(AF_INET, SOCK_STREAM)
            tcp_socket.connect((ip, 666))
            tcp_socket.settimeout(.001)

            while self.running and ip in self.servers_clients:
                try:
                    message = tcp_socket.recv(1024).decode()
                    if message.startswith("GET_XY"):
                        coordinates = message[7:]
                        x, y = map(int, coordinates.split(','))
                        pyautogui.FAILSAFE = False
                        pyautogui.moveTo(x, y)
                        pyautogui.click(x, y)
                        pyautogui.FAILSAFE = True
                        continue
                except timeout:
                    continue
        except Exception as e:
            print(f"Failed to connect or receive coordinates: {e} from {ip}", flush=True)
            close_cleanup()
        finally:
            close_cleanup()

    def tcp_send_to_clients(self, coordinates):
        for client_socket in self.server_clients_sockets_list.copy():
            ip = client_socket.getpeername()[0]
            if ip in self.servers_clients.copy():
                try:
                    client_socket.send(coordinates.encode())
                except Exception as e:
                    print(f"Failed to send coordinates to client {ip}: {e}", flush=True)
                    client_socket.close()
                    with self.lock:
                        self.server_clients_sockets_list.remove(client_socket)
                        if ip in self.servers_clients:
                            self.servers_clients.remove(ip)
                            self.servers_clients_event.set()
            else:
                client_socket.close()
                with self.lock:
                    self.server_clients_sockets_list.remove(client_socket)

class CursorSyncApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.running = True
        self.cursor_sync = CursorSync(self)
        self.network_operations = NetworkOperations(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Cursor Synchronizer")
        self.setGeometry(100, 100, 400, 200)
        self.setMinimumSize(225, 160)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        screen = self.screen()
        screen_rect = screen.geometry()
        max_value_x = screen_rect.width() - 1
        max_value_y = screen_rect.height() - 1
        self.x_input = QLineEdit()
        self.x_input.setValidator(QIntValidator(0, max_value_x))
        self.x_input.setPlaceholderText(f"min 0, max {max_value_x}")
        self.y_input = QLineEdit()
        self.y_input.setValidator(QIntValidator(0, max_value_y))
        self.y_input.setPlaceholderText(f"min 0, max {max_value_y}")
        main_layout.addWidget(QLabel("X:"))
        main_layout.addWidget(self.x_input)
        main_layout.addWidget(QLabel("Y:"))
        main_layout.addWidget(self.y_input)

        self.button = QPushButton("Locate coordinates", self)
        self.button.clicked.connect(self.start_crosshair)
        main_layout.addWidget(self.button)

        self.go_button = QPushButton("Go!")
        self.go_button.installEventFilter(self)
        main_layout.addWidget(self.go_button)

        self.setCentralWidget(main_widget)

    def eventFilter(self, watched, event):
        if watched == self.go_button and event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            if not self.x_input.hasAcceptableInput() and not self.y_input.hasAcceptableInput():
                QToolTip.showText(QCursor.pos(), "Invalid X and Y values.", self.go_button, self.go_button.rect(), 2000)
                return True
            elif not self.x_input.hasAcceptableInput():
                QToolTip.showText(QCursor.pos(), "Invalid X value.", self.go_button, self.go_button.rect(), 2000)
                return True
            elif not self.y_input.hasAcceptableInput():
                QToolTip.showText(QCursor.pos(), "Invalid Y value.", self.go_button, self.go_button.rect(), 2000)
                return True
            else:
                self.cursor_sync.move_cursor()
                return True        
        elif watched == self.go_button and event.type() == QEvent.KeyPress and event.key() == Qt.Key_Space:
            tooltip_text = ""
            if not self.x_input.hasAcceptableInput() and not self.y_input.hasAcceptableInput():   
                tooltip_text = "Invalid X and Y values."   
            elif not self.x_input.hasAcceptableInput():   
                tooltip_text = "Invalid X value."   
            elif not self.y_input.hasAcceptableInput():   
                tooltip_text = "Invalid Y value."   
            else:   
                self.cursor_sync.move_cursor()
                return True

            label = QLabel()
            label.setFont(QToolTip.font())
            label.setText(tooltip_text)
            label.adjustSize()

            button_center = self.go_button.mapToGlobal(self.go_button.rect().center())

            tooltip_position = QPoint(button_center.x() - (label.width() + 15) // 2, button_center.y() - label.height() // 2)
            QToolTip.showText(tooltip_position, tooltip_text, self.go_button, self.go_button.rect(), 2000)   
            return True   
        return super().eventFilter(watched, event)

    def start_crosshair(self):
        self.button.setText("Waiting for click...")
        self.button.setEnabled(False)
        self.crosshair_window = CrosshairWindow(self)
        self.crosshair_window.showFullScreen()

    def reset_button(self):
        self.button.setText("Locate coordinates")
        self.button.setEnabled(True)
        button_center = self.button.mapToGlobal(QPoint(self.button.width() // 2, self.button.height() // 2))
        pyautogui.FAILSAFE = False
        pyautogui.moveTo(button_center.x(), button_center.y())
        pyautogui.FAILSAFE = True

    def send_stop_message(self):
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        message = "STOP_SERVER"

        udp_socket.sendto(message.encode(), ('<broadcast>', 666))
        print("Broadcasted stop message to", '<broadcast>', flush=True)
        udp_socket.close()

    def closeEvent(self, event):
        self.hide()
        self.running = False
        self.send_stop_message()
        self.network_operations.servers_clients_event.set()

        fake_socket_for_closing = socket(AF_INET, SOCK_STREAM)
        fake_socket_for_closing.connect(('localhost', 666))
        fake_socket_for_closing.close()

        for thread in threading.enumerate():
            if thread is not threading.main_thread():
                thread.join()

        event.accept()

class CrosshairWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMouseTracking(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.crosshair_color = QColor(0, 255, 0)
        self.crosshair_pen = QPen(self.crosshair_color)
        self.crosshair_pen.setWidth(1)

    def paintEvent(self, event):
        painter = QPainter(self)

        screen_rect = QApplication.desktop().screenGeometry()
        width, height = screen_rect.width(), screen_rect.height()

        cursor_pos = self.mapFromGlobal(QApplication.desktop().cursor().pos())

        painter.fillRect(screen_rect, QColor(0, 0, 0, 1))

        painter.setPen(self.crosshair_pen)
        painter.drawLine(0, cursor_pos.y(), width, cursor_pos.y())
        painter.drawLine(cursor_pos.x(), 0, cursor_pos.x(), height)

    def mouseMoveEvent(self, event):
        time.sleep(.005)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.pos().x()
            y = event.pos().y()
            print(f"Located at {x}, {y}", flush=True)
            self.parent().x_input.setText(str(x))
            self.parent().y_input.setText(str(y))
            self.close()
            self.parent().reset_button()
            self.deleteLater()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            self.parent().reset_button()
            self.deleteLater()

if __name__ == "__main__":
    Sync_App = QApplication(sys.argv)
    Sync_App.setWindowIcon(QIcon(resource_path('icon.ico')))
    Cursor_Sync_App = CursorSyncApp()
    Cursor_Sync_App.show()

    threading.Thread(target=Cursor_Sync_App.network_operations.broadcast_listener, name='broadcast_listener').start()
    threading.Thread(target=Cursor_Sync_App.network_operations.broadcast_start_sender, name='broadcast_start_sender').start()
    threading.Thread(target=Cursor_Sync_App.network_operations.tcp_server_start, name='tcp_server_start').start()
    threading.Thread(target=Cursor_Sync_App.network_operations.tcp_clients_start, name='tcp_clients_start').start()

    sys.exit(Sync_App.exec_())
