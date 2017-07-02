import sys
import math
from random import randint
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsLineItem
from PyQt5.QtGui import QColor
from interface import Ui_MainWindow
from charge import Charge
from events import Events

DEFAULT_RADIUS = 40
MIN_CHARGE_VALUE = -20
MAX_CHARGE_VALUE = 20


class ChargeSystem:
    """
    Класс, содержащий реализующийграфический пользовательский интерфейс и содержащий все обработчики событий от него
    """
    def __init__(self):
        app = QtWidgets.QApplication(sys.argv)
        MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(MainWindow)
        MainWindow.show()

        # Стандартные характеристики зарядов
        self.radius = DEFAULT_RADIUS
        self.min_width = self.min_height = self.radius
        self.max_width = self.ui.graphicsView.width() - self.radius
        self.max_height = self.ui.graphicsView.height() - self.radius
        self.max_color_value = 0

        # Инициализируем графическую сцену и привязываем её к graphicsView
        self.scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)

        # Выделенные заряды на сцене
        self.selected_charges = []

        # Создаём экземпляр класса событий
        self.events = Events()
        self.events.focus_in_event[Charge].connect(self.enable_editing)
        self.events.focus_out_event.connect(self.disable_editing)
        self.events.mouse_press_event[Charge].connect(self.delete_connections)
        self.events.mouse_release_event.connect(self.add_connections)

        # Инициализируем обработчики событий от элементов пользовательского интерейса
        self.ui.addCharge.clicked.connect(self.add_charge)
        self.ui.deleteCharge.clicked.connect(self.delete_charge)
        self.ui.chargeValue.editingFinished.connect(self.change_charge_value)

        # Запускаем бесконечный цикл обработки событий от пользовательского интерфейса
        sys.exit(app.exec_())

    def add_charge(self):
        """ Обработчик нажатия на кнопку add_charge, добавляет заряд на graphicsView """
        charge_value = randint(MIN_CHARGE_VALUE, MAX_CHARGE_VALUE)
        color = self.identify_color(charge_value)

        charge = Charge(randint(self.min_width, self.max_width), randint(self.min_height, self.max_height),
                        self.radius, self.radius, charge_value, color, self.events)
        charge.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)

        # Снимаем выделение со всех зарядов и выделяем только вновь добавленный
        for selected_charge in self.scene.selectedItems():
            if type(selected_charge) == Charge:
                selected_charge.setSelected(False)
        charge.setSelected(True)

        # Добавляем сам новый заряд и его значение
        self.scene.addItem(charge)
        charge.setFocus()

        # Добавляем связи со всеми существующими на данный момент зарядами
        self.selected_charges = self.scene.selectedItems()
        self.add_connections()

    def delete_charge(self):
        """ Обработчик нажатия на кнопку delete_charge, удаляем выбранные заряды с graphicsView """
        # Удаляем все связи с выбранными зарядами
        for selected_charge in self.scene.selectedItems():
            for connection in selected_charge.connections:
                self.scene.removeItem(connection)

        # Находим максимальный по модулю заряд из всех удаляемых
        deleted_charge_values = [abs(selected_charge.charge_value) for selected_charge in self.scene.selectedItems()]
        max_deleted_charge_value = max(deleted_charge_values)

        # Удаляем выделенные заряды и делаем недоступными элементы редактирования
        for selected_charge in self.scene.selectedItems():
            self.scene.removeItem(selected_charge)

        self.disable_editing()

        # Смотрим, не был ли его заряд максимальным среди всех (иначе нужно менять цвета всех оставшихся)
        if abs(max_deleted_charge_value) == self.max_color_value:
            self.repaint_charges()

        # Отображаем значение энергии системы зарядов, если на graphicsView минимум 2 заряда
        # (т.е. 3 элемента: 2 заряда + 1 соединение)
        if len(self.scene.items()) >= 3:
            self.update_energy()
        else:
            self.ui.systemEnergy.setText("")

    def enable_editing(self, charge):
        """ Функция, делающая доступной работу с зарядом (зарядами) при его (их) выделении """
        self.ui.chargeValue.setText("{}".format(charge.charge_value))
        self.ui.chargeValue.setEnabled(True)
        self.ui.deleteCharge.setEnabled(True)

    def disable_editing(self):
        """ Функция, делающая недоступной работу с зарядом (зарядами) при снятии выделения """
        if not self.ui.chargeValue.hasFocus():
            self.ui.chargeValue.setText("")
            self.ui.chargeValue.setEnabled(False)
            self.ui.deleteCharge.setEnabled(False)

    def change_charge_value(self):
        """ Обработчик изменения значения величины заряда (зарядов) """
        charge_value = int(self.ui.chargeValue.text())
        for selected_charge in self.scene.selectedItems():
            if type(selected_charge) == Charge:
                selected_charge.set_charge_value(charge_value)
        self.ui.chargeValue.clearFocus()

        # Перекрашиваем все заряды, если изменилось максимальное значение величины заряда
        if self.max_color_value < abs(charge_value):
            self.max_color_value = abs(charge_value)
            for item in self.scene.items():
                if type(item) == Charge:
                    color = self.identify_color(item.charge_value)
                    item.setBrush(color)
        else:
            self.repaint_charges()

    def identify_color(self, charge_value):
        """ Функция, определяющая цвет зарядов в зависимости от величины максимального заряда из всех """
        if self.max_color_value < abs(charge_value):
            self.max_color_value = abs(charge_value)

        # Задаём цвет заряда в зависимости от его величины
        if abs(charge_value) > self.max_color_value * 6 / 7:
            color = QColor(229, 25, 25)
        elif abs(charge_value) > self.max_color_value * 5 / 7:
            color = QColor(249, 107, 24)
        elif abs(charge_value) > self.max_color_value * 4 / 7:
            color = QColor(249, 188, 23)
        elif abs(charge_value) > self.max_color_value * 3 / 7:
            color = QColor(23, 249, 94)
        elif abs(charge_value) > self.max_color_value * 2 / 7:
            color = QColor(23, 215, 249)
        elif abs(charge_value) > self.max_color_value / 7:
            color = QColor(23, 98, 249)
        else:
            color = QColor(139, 23, 249)

        return color

    def repaint_charges(self):
        """ Функция, перерисовывающая заряды """
        self.max_color_value = 0
        for item in self.scene.items():
            if type(item) == Charge:
                if abs(item.charge_value) > self.max_color_value:
                    self.max_color_value = abs(item.charge_value)

        for item in self.scene.items():
            if type(item) == Charge:
                color = self.identify_color(item.charge_value)
                item.setBrush(color)

    def update_energy(self):
        """ Функция, пересчитывающая энергию системы и обновляющая эначение соответствующего поля """
        energy = 0
        for item1 in self.scene.items():
            for item2 in self.scene.items():
                if item1 != item2 and type(item1) == Charge and type(item2) == Charge:
                    distance = math.sqrt((item1.x() - item2.x()) ** 2 + (item1.y() - item2.y()) ** 2)
                    if distance != 0:
                        energy += item1.charge_value * item2.charge_value / distance

        # Коэффициент k / 2 в формуле
        energy *= 4.49
        self.ui.systemEnergy.setText("{:.2f} * 10^9".format(energy))

    def add_connections(self):
        """ Функция, добавляющая соединения всем выделенным зарядам """
        for selected_charge in self.selected_charges:
            for item in self.scene.items():
                if type(item) == Charge and selected_charge != item:
                    connection = QGraphicsLineItem(selected_charge.x() + selected_charge.rect().width() / 2,
                                                   selected_charge.y() + selected_charge.rect().height() / 2,
                                                   item.x() + item.rect().width() / 2,
                                                   item.y() + item.rect().height() / 2)
                    selected_charge.add_connection(connection)
                    item.add_connection(connection)
                    self.scene.addItem(connection)

        # Отображаем значение энергии системы зарядов, если на graphicsView минимум 2 заряда
        # (т.е. 3 элемента: 2 заряда + 1 соединение)
        if len(self.scene.items()) >= 3:
            self.update_energy()

        # Оцищаем список зарядов, для которых мы должны были перерисовать соединения
        self.selected_charges = []

    def delete_connections(self, charge):
        """ Функция, удаляющая соединения всем выделенным зарядам """
        for selected_charge in self.scene.selectedItems():
            if type(selected_charge) == Charge:
                # Сохраняем список зарядов, для которых мы удалили соединения, чтобы топом их перерисовать
                self.selected_charges.append(selected_charge)
                for connection in selected_charge.connections:
                    self.scene.removeItem(connection)

        # Проверяем, находится ли заряд, на котором фокус, в списке выделенных (возможно, что нет)
        if charge not in self.scene.selectedItems():
            # Добавляем данный заряд в список
            self.selected_charges.append(charge)
            for connection in charge.connections:
                self.scene.removeItem(connection)


if __name__ == "__main__":
    chargeSystem = ChargeSystem()




