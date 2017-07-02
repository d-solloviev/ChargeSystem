from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtGui import QPen, QBrush, QColor


class Charge(QGraphicsEllipseItem):
    """
    Класс, описывающий заряд, представленный эллипсон на graphicsView
    """
    def __init__(self, x, y, radius_x, radius_y, charge_value, color, events):
        super(Charge, self).__init__(0, 0, radius_x, radius_y)
        self.setPen(QPen(QColor(0, 0, 0)))
        self.setBrush(QBrush(color))
        self.setX(x)
        self.setY(y)
        self.charge_value = charge_value
        self.events = events
        self.connections = []
        self.setAcceptTouchEvents(True)
        self.base_x = x
        self.base_y = y

    def focusInEvent(self, *args, **kwargs):
        """ Обработчик события попадания заряда в фокус """
        self.events.focus_in_event.emit(self)

    def focusOutEvent(self, *args, **kwargs):
        """ Обработчик события выхода заряда из фокуса """
        self.events.focus_out_event.emit()

    def mousePressEvent(self, *args, **kwargs):
        """ Обработчик события нажатия на заряд """
        QGraphicsEllipseItem.mousePressEvent(self, *args, **kwargs)
        self.events.mouse_press_event.emit(self)

    def mouseReleaseEvent(self, *args, **kwargs):
        """ Обработчик события отпускания мыши """
        QGraphicsEllipseItem.mouseReleaseEvent(self, *args, **kwargs)
        self.events.mouse_release_event.emit()

    def add_connection(self, connection):
        """ Функция, добавляющая указанную связь в список связей текущего заряда """
        self.connections.append(connection)

    def set_charge_value(self, charge_value):
        """ Функция, задающая величину заряда """
        self.charge_value = charge_value
