import sys
import json
from PyQt5 import QtCore, QtGui, QtWidgets


class Crosshair(QtWidgets.QWidget):
    def __init__(self, parent=None, windowSize=24, penWidth=2):
        QtWidgets.QWidget.__init__(self, parent)
        self.ws = windowSize
        self.pen = QtGui.QPen(QtGui.QColor(0, 255, 0, 255))
        self.pen.setWidth(penWidth)
        self.load_configuration()  # Load Settings json
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowTransparentForInput)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.update_position()

    def load_configuration(self, file_path=None):
        try:
            if file_path:
                with open(file_path, 'r') as f:
                    config = json.load(f)
                    self.ws = config.get('windowSize', self.ws)
                    self.pen.setWidth(config.get('penWidth', self.pen.width()))
                    color = config.get('color', [0, 255, 0, 255])
                    self.pen.setColor(QtGui.QColor(*color))
            else:
                with open('crosshair_config.json', 'r') as f:
                    config = json.load(f)
                    self.ws = config.get('windowSize', self.ws)
                    self.pen.setWidth(config.get('penWidth', self.pen.width()))
                    color = config.get('color', [0, 255, 0, 255])
                    self.pen.setColor(QtGui.QColor(*color))
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save_configuration(self, file_path):
        config = {
            'windowSize': self.ws,
            'penWidth': self.pen.width(),
            'color': [self.pen.color().red(), self.pen.color().green(), self.pen.color().blue(), self.pen.color().alpha()]
        }
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=4)

    def update_position(self):
        screen_center = QtWidgets.QApplication.desktop().screen().rect().center()
        self.move(screen_center - QtCore.QPoint(int(self.ws / 2), int(self.ws / 2)))

    def paintEvent(self, event):
        ws = self.ws
        d = 6
        painter = QtGui.QPainter(self)
        painter.setPen(self.pen)
        painter.drawLine(int(ws / 2), 0, int(ws / 2), int(ws / 2 - ws / d))   # Top
        painter.drawLine(int(ws / 2), int(ws / 2 + ws / d), int(ws / 2), ws)   # Bottom
        painter.drawLine(0, int(ws / 2), int(ws / 2 - ws / d), int(ws / 2))   # Left
        painter.drawLine(int(ws / 2 + ws / d), int(ws / 2), ws, int(ws / 2))   # Right


class ConfigWindow(QtWidgets.QWidget):
    def __init__(self, crosshair_widget):
        super().__init__()
        self.crosshair_widget = crosshair_widget
        self.setWindowTitle('Crosshair Configuration')
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # Window Size Slider and SpinBox
        self.window_size_label = QtWidgets.QLabel('Window Size')
        self.window_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.window_size_slider.setMinimum(10)
        self.window_size_slider.setMaximum(100)
        self.window_size_slider.setValue(self.crosshair_widget.ws)
        self.window_size_slider.valueChanged.connect(self.update_crosshair)

        self.window_size_spinbox = QtWidgets.QSpinBox()
        self.window_size_spinbox.setMinimum(10)
        self.window_size_spinbox.setMaximum(100)
        self.window_size_spinbox.setValue(self.crosshair_widget.ws)
        self.window_size_spinbox.valueChanged.connect(self.update_crosshair)

        self.layout.addWidget(self.window_size_label)
        self.layout.addWidget(self.window_size_slider)
        self.layout.addWidget(self.window_size_spinbox)

        # Pen Width Slider and SpinBox
        self.pen_width_label = QtWidgets.QLabel('Pen Width')
        self.pen_width_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.pen_width_slider.setMinimum(1)
        self.pen_width_slider.setMaximum(10)
        self.pen_width_slider.setValue(self.crosshair_widget.pen.width())
        self.pen_width_slider.valueChanged.connect(self.update_crosshair)

        self.pen_width_spinbox = QtWidgets.QSpinBox()
        self.pen_width_spinbox.setMinimum(1)
        self.pen_width_spinbox.setMaximum(10)
        self.pen_width_spinbox.setValue(self.crosshair_widget.pen.width())
        self.pen_width_spinbox.valueChanged.connect(self.update_crosshair)

        self.layout.addWidget(self.pen_width_label)
        self.layout.addWidget(self.pen_width_slider)
        self.layout.addWidget(self.pen_width_spinbox)

        # Color Picker
        self.color_label = QtWidgets.QLabel('Color')
        self.color_picker = QtWidgets.QPushButton('Select Color')
        self.color_picker.clicked.connect(self.select_color)
        self.layout.addWidget(self.color_label)
        self.layout.addWidget(self.color_picker)

        # Save Button
        self.save_button = QtWidgets.QPushButton('Save Configuration')
        self.save_button.clicked.connect(self.save_configuration_dialog)
        self.layout.addWidget(self.save_button)

        # Load Button
        self.load_button = QtWidgets.QPushButton('Load Configuration')
        self.load_button.clicked.connect(self.load_configuration_dialog)
        self.layout.addWidget(self.load_button)

        # Connect close event to hide the window instead of closing it
        self.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
        self.closeEvent = self.hideEvent

    def update_crosshair(self):
        window_size = self.window_size_slider.value()
        pen_width = self.pen_width_slider.value()
        self.crosshair_widget.ws = window_size
        self.crosshair_widget.pen.setWidth(pen_width)
        self.crosshair_widget.update()
        self.crosshair_widget.update_position()

        # Update SpinBox values
        self.window_size_spinbox.setValue(window_size)
        self.pen_width_spinbox.setValue(pen_width)

    def select_color(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.crosshair_widget.pen.setColor(color)
            self.crosshair_widget.update()

    def save_configuration_dialog(self):
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, 'Save Configuration', '', 'JSON Files (*.json)')
        if file_path:
            self.crosshair_widget.save_configuration(file_path)

    def load_configuration_dialog(self):
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Load Configuration', '', 'JSON Files (*.json)')
        if file_path:
            self.crosshair_widget.load_configuration(file_path)
            self.window_size_slider.setValue(self.crosshair_widget.ws)
            self.pen_width_slider.setValue(self.crosshair_widget.pen.width())
            self.update_crosshair()  # Apply Settings

    def hideEvent(self, event):
        self.hide()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    crosshair_widget = Crosshair(windowSize=24, penWidth=2)
    crosshair_widget.show()

    config_window = ConfigWindow(crosshair_widget)
    config_window.show()

    sys.exit(app.exec_())
