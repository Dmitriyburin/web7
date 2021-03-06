import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QComboBox, QAction
from PyQt5 import QtCore
import os
from search import Search

SCREEN_SIZE = [600, 450]


class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.point = Search()
        self.param = self.point.point_param
        self.type_map = {'map': 'Схема', 'sat': 'Спутник', 'sat,skl': 'Гибрид'}
        self.map = 'map'
        self.map_file = self.point.map_api(self.param)
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.draw_map()

    def draw_map(self):
        self.param = {
            "ll": ",".join(map(str, self.point.ll)),
            "spn": ",".join(map(str, self.point.spn)),
            "l": self.map,
            # "pt": ",".join(map(str, point.ll))
        }
        self.map_file = self.point.map_api(self.param)

        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap.scaled(600, 450))
        self.image.setPixmap(self.pixmap)

    def keyPressEvent(self, event):  # Обработка клавиш

        if event.key() == QtCore.Qt.Key.Key_Up:
            self.point.ll = (self.point.ll[0], self.point.ll[1] + self.point.spn[1])
        if event.key() == QtCore.Qt.Key.Key_Down:
            self.point.ll = (self.point.ll[0], self.point.ll[1] - self.point.spn[1])
        if event.key() == QtCore.Qt.Key.Key_Left:
            self.point.ll = (self.point.ll[0] - self.point.spn[0], self.point.ll[1])
        if event.key() == QtCore.Qt.Key.Key_Right:
            self.point.ll = (self.point.ll[0] + self.point.spn[0], self.point.ll[1])

        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()

        self.draw_map()
        event.accept()

    def wheelEvent(self, event):
        angle = event.angleDelta() / 8
        angleY = angle.y()

        if angleY > 0:
            if self.point.spn[0] > 0.001:
                self.point.spn = (self.point.spn[0] / 2, self.point.spn[1] / 2)
        else:
            if self.point.spn[0] < 0.6:
                self.point.spn = (self.point.spn[0] * 2, self.point.spn[1] * 2)

        self.draw_map()

    def eventFilter(self, source, event):
        if event.type() == QtCore.Qt.Key.Key_Right:
            print('нажалось')

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
