from PyQt5.QtCore import QObject, pyqtSignal
from charge import Charge


class Events(QObject):
    """
    Класс, включающий используемые события от взаимодействия пользователя с задярами
    """
    focus_in_event = pyqtSignal(Charge)
    focus_out_event = pyqtSignal()
    mouse_press_event = pyqtSignal(Charge)
    mouse_release_event = pyqtSignal()
