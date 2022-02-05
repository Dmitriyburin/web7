import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QComboBox, QLineEdit, QCheckBox
from PyQt5.QtCore import Qt
from os import remove
from search import Search
from geocoder import geocode

SCREEN_SIZE = [600, 550]


class LineEdit(QLineEdit):
    def keyPressEvent(self, event):
        if event.key() in (
                Qt.Key.Key_Right,
                Qt.Key.Key_Left
        ):
            event.ignore()
        else:
            super(LineEdit, self).keyPressEvent(event)


class ComboBox(QComboBox):
    def keyPressEvent(self, event):
        if event.key() in (
                Qt.Key.Key_Up,
                Qt.Key.Key_Down
        ):
            event.ignore()
        else:
            super(ComboBox, self).keyPressEvent(event)


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.postal_code = False
        self.point_selected = ''
        self.point = Search()
        self.param = self.point.point_param
        self.type_map = {'map': 'Схема', 'sat': 'Спутник', 'sat,skl': 'Гибрид'}
        self.map = 'map'
        self.map_file = self.point.map_api(self.param)
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.name_object = LineEdit(self)
        self.name_object.move(0, 450)
        self.name_object.resize(200, 25)
        self.btn = QPushButton('Поиск', self)
        self.btn.resize(100, 25)
        self.btn.move(250, 450)
        self.btn.clicked.connect(self.search_object)

        self.btn = QPushButton('Сбросить', self)
        self.btn.resize(100, 25)
        self.btn.move(350, 450)
        self.btn.clicked.connect(self.clear_object)

        cb = QCheckBox('Почтовый индекс', self)
        cb.move(450, 450)
        cb.stateChanged.connect(self.change_postal_code)

        self.full_name = QLabel(self)
        self.full_name.move(0, 500)
        self.full_name.resize(SCREEN_SIZE[0], 25)
        self.full_name.setVisible(False)

        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.draw_map()

        self.combo = ComboBox(self)
        for el in list(self.type_map):
            self.combo.addItem(self.type_map[el])
        self.combo.currentTextChanged.connect(self.set_l)
        self.combo.move(10, 10)

    def mousePressEvent(self, event):
        '''Но это не будет работать если мы перейдем к другому полушарию, только для северо-восточного полушария'''
        print(self.point.spn)
        print(f"Координаты(широта, высота): {self.point.ll[1] - (event.y() - 225) * self.point.spn[1] / 450}, "
              f"{self.point.ll[0] + (event.x() - 300) * self.point.spn[0] / 600}")

    def change_postal_code(self, event):
        if event == Qt.Checked:
            self.postal_code = True
            self.full_name.setText(self.full_name_object[0] + '; ' + self.full_name_object[1])
        else:
            self.postal_code = False
            self.full_name.setText(self.full_name_object[0])

    def clear_object(self):
        self.name_object.setText('')
        self.point_selected = ''
        self.full_name.setVisible(False)
        self.draw_map()

    def search_object(self):
        self.point = Search(self.name_object.text())

        self.param = self.point.point_param
        self.map_file = self.point.map_api(self.param)
        self.point_selected = self.point.ll
        self.full_name_object = self.point.full_name
        text = self.full_name_object[0]
        if self.full_name_object[1]:
            text += '; ' + self.full_name_object[1] if self.postal_code else\
                self.full_name_object[0]

        self.full_name.setText(text)
        self.full_name.setVisible(True)
        self.draw_map(pt=self.point.point_param['pt'])

    def draw_map(self, pt=""):
        if self.point_selected:
            print(self.point.spn)
            x1, x2 = self.point.ll[0] - self.point.ll[0] * self.point.spn[0], self.point.ll[0] + self.point.ll[0] *\
                     self.point.spn[0]
            y1, y2 = self.point.ll[1] - self.point.ll[1] * self.point.spn[1], self.point.ll[1] + self.point.ll[1] *\
                     self.point.spn[1]
            if x1 < self.point_selected[0] < x2 and y1 < self.point_selected[1] < y2:
                pt = ",".join(map(str, self.point_selected))
        self.param = {
            "ll": ",".join(map(str, self.point.ll)),
            "spn": ",".join(map(str, self.point.spn)),
            "l": self.map,
            "pt": pt
        }
        self.map_file = self.point.map_api(self.param)

        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap.scaled(600, 450))
        self.image.setPixmap(self.pixmap)

    def keyPressEvent(self, event):  # Обработка клавиш
        print('здеся')

        if event.key() == Qt.Key.Key_Up:
            self.point.ll = (self.point.ll[0], self.point.ll[1] + self.point.spn[1])
        if event.key() == Qt.Key.Key_Down:
            self.point.ll = (self.point.ll[0], self.point.ll[1] - self.point.spn[1])
        if event.key() == Qt.Key.Key_Left:
            self.point.ll = (self.point.ll[0] - self.point.spn[0], self.point.ll[1])
        if event.key() == Qt.Key.Key_Right:
            self.point.ll = (self.point.ll[0] + self.point.spn[0], self.point.ll[1])

        if event.key() == Qt.Key.Key_Escape:
            self.close()

        self.draw_map()
        event.accept()

    def set_l(self):
        self.map = list(self.type_map)[self.combo.currentIndex()]
        self.draw_map()

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

    def mousePressEvent(self, event):
        if event.button() == 1:  # Нажатие ПКМ
            x, y = event.pos().x(), event.pos().y()
            pos_change = SCREEN_SIZE[0] // 2 - x, (SCREEN_SIZE[1] - 100) // 2 - y
            degrees = self.point.ll[0] - (self.point.spn[0] / 380 * pos_change[0]),\
                      self.point.ll[1] + (self.point.spn[1] / 380 * pos_change[1])

            self.point = Search(f'{degrees[0]},{degrees[1]}', spn=self.point.spn)

            # метка ставится ровно в той точке, куда нажали (если удалить, метка будет привязана к объекту
            self.point.ll = degrees
            self.param = self.point.point_param
            self.map_file = self.point.map_api(self.param)

            self.point_selected = self.point.ll
            self.full_name_object = self.point.full_name

            text = self.full_name_object[0]
            if self.full_name_object[1]:
                text += '; ' + self.full_name_object[1] if self.postal_code else\
                    self.full_name_object[0]

            self.full_name.setText(text)
            self.full_name.setVisible(True)

            self.draw_map(pt=f'{degrees[0]},{degrees[1]}')

    def eventFilter(self, source, event):
        if event.type() == Qt.Key.Key_Right:
            print('нажалось')

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        remove(self.map_file)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
