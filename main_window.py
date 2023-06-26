import serial.tools.list_ports

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QMessageBox

from pyqtgraph import PlotWidget, mkPen
from serial_data_receiver import SerialDataReceiver

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VizhPort")
        self.setGeometry(0, 0, 500, 500)
        self.center_window()
        self.setWindowIcon(QIcon("assets/vizhport.ico"))

        self.serial_ports = []
        self.baud_rates = ["300", "600", "750", "1200", "2400",
            "4800", "9600", "14400", "19200", "31250", "38400",
            "57600", "74880", "115200", "230400", "250000",
            "460800", "500000", "921600", "1000000", "2000000"]

        self.port_label = QLabel("Serial Ports")
        self.port_dropdown = QComboBox()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_serial_ports)

        self.baudrate_label = QLabel("Baud rate")
        self.baudrate_dropdown = QComboBox()
        self.baudrate_dropdown.addItems(self.baud_rates)
        self.baudrate_dropdown.setCurrentText("9600")

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_serial)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_serial)

        self.plot_widget = PlotWidget()
        self.plot_widget.setMinimumSize(300, 300)
        self.plot_widget.showGrid(False, True, alpha=0.5)

        self.x = []
        self.y = []
        self.serial_thread = None

        self.setup_ui()
        self.refresh_serial_ports()

    def get_available_serial_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports

    def setup_ui(self):
        widget = QWidget(self)
        self.setCentralWidget(widget)

        main_layout = QVBoxLayout(widget)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.port_label)
        top_layout.addWidget(self.port_dropdown)
        top_layout.addWidget(self.refresh_button)
        top_layout.addSpacing(35)
        top_layout.addWidget(self.baudrate_label)
        top_layout.addWidget(self.baudrate_dropdown)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.plot_widget)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch(1)

        main_layout.addLayout(button_layout)

    def refresh_serial_ports(self):
        self.serial_ports = self.get_available_serial_ports()
        self.port_dropdown.clear()
        self.port_dropdown.addItems(self.serial_ports)

    def start_serial(self):
        selected_port = self.port_dropdown.currentText()
        selected_baudrate = int(self.baudrate_dropdown.currentText())

        if not selected_port:
            error_message = "Please select a serial port."
            self.show_message_dialog("Serial Port Error", error_message)
            return

        self.stop_serial()
        self.x = []
        self.y = []

        self.serial_thread = SerialDataReceiver(selected_port, selected_baudrate)
        self.serial_thread.data_received.connect(self.update_graph)
        self.serial_thread.start()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_serial(self):
        if self.serial_thread and self.serial_thread.isRunning():
            self.serial_thread.stop()
            self.serial_thread.wait()

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_graph(self, data):
        self.x.append(len(self.x))
        self.y.append(data)

        pen = mkPen(color="g", width=2)
        self.plot_widget.plot(self.x, self.y, pen=pen, clear=True)

    def show_message_dialog(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def center_window(self):
        frame = self.frameGeometry()
        center_point = QtWidgets.QDesktopWidget().availableGeometry().center()

        frame.moveCenter(center_point)
        self.move(frame.topLeft())
