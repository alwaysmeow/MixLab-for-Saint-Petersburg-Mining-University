from PyQt5.QtWidgets import QMessageBox, QDateEdit, QWidget, QDialog, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt, QDate
from table import *
from test_window import TestWindow
from toolsFunctions import *

class ChoiceTable(QDialog):
    def __init__(self, DataBase, type):
        super().__init__()
        self.DataBase = DataBase
        self.cursor = self.DataBase.cursor()
        self.type = type
        self.setWindowTitle("Выбор реагента")

        layout = QVBoxLayout()

        self.QTable = QTableWidget()
        self.QTable.setColumnCount(7)
        self.QTable.setHorizontalHeaderLabels(["Тип", "Название", "Производитель", "Удельный вес", "Первичные свойства", "Вторичные свойства", "Рабочие концентрации", ""]) # заменить на человеческие
        self.QTable.resizeColumnToContents(4)
        self.QTable.resizeColumnToContents(5)
        self.QTable.resizeColumnToContents(6)
        self.cursor.execute(f"select {columnsNames(reagentsColumns[1:])} from Reagents where type = '{type}'")
        self.data = self.cursor.fetchall()
        self.QTable.setRowCount(len(self.data))
        for i in range(len(self.data)):
            for j in range(7):
                self.QTable.setItem(i, j, QTableWidgetItem(str(self.data[i][j])))

        self.QTable.cellClicked.connect(self.Choice)
        self.QTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout.addWidget(self.QTable)
        self.setLayout(layout)
        self.setFixedSize(870, 400)
    
    def Choice(self, result):
        self.cursor.execute(f"select id, name, density from Reagents where name = '{QTableWidgetItem(str(self.data[self.QTable.currentRow()][1])).text()}' and type = '{self.type}'")
        self.result = list(self.cursor.fetchone())
        self.accept()

class CompoundForm(QWidget):
    def __init__(self, DataBase, mainWindow):
        super().__init__()
        self.setWindowTitle("Создание смеси")
        
        self.DataBase = DataBase
        self.mainWindow = mainWindow
        self.cursor = self.DataBase.cursor()
        self.id = 1

        self.cementId = -1
        self.additivesIds = []
        self.calculated = False
        self.cementConnection = -1
        self.additionConnections = []
        self.cementReagent = -1
        self.additiveReagents = []
        self.compound = -1

        self.labels1 = ["Дата", "Заказчик", "Тип операции", "Диаметр ОК, мм", "Тип раствора", "Время нагрева, мин"]
        self.labels2 = ["Статическая температура, °C", "Циркуляционная температура, °C", "Давление, psi", "Плотность, г/см3", "Выход по цементу", "В/Ц", "Выход смеси", "Водосмесевое", "Масса цемента для теста, г", "Объем готового раствора"]
        self.labels3 = ["Материал", "% от веса цемента", "Удельный вес, г/см^3", "К1", "Масса на 1 м3, кг", "Объем", "Вес для теста, гр", "Объем добавок, мл"]

        self.head = QHBoxLayout()
        self.body = QVBoxLayout()
        self.buttons = QHBoxLayout()

        self.grid1 = QGridLayout()
        for i in range(len(self.labels1)):
            if i == 0:
                edit = QDateEdit()
                edit.setDate(QDate.currentDate())
            elif i == 2:
                edit = QTextEdit()
                edit.setMaximumHeight(50)
            else:
                edit = QLineEdit()
            self.grid1.addWidget(QLabel(self.labels1[i]), i, 0)
            self.grid1.addWidget(edit, i, 1)
        self.grid1.setRowStretch(6, 1)

        self.grid2 = QGridLayout()
        for i in range(len(self.labels2)):
            self.grid2.addWidget(QLabel(self.labels2[i]), i, 0)
            edit = QLineEdit()
            if i > 3 and i < 8 or i == 9:
                setInactive(edit)
            self.grid2.addWidget(edit, i, 1)
            if i < 8:
                edit = QLineEdit()
                setInactive(edit)
                self.grid2.addWidget(edit, i, 2)

        self.grid3 = QGridLayout()
        for i in range(len(self.labels3)):
            self.grid3.addWidget(QLabel(self.labels3[i]), 0, i)
            if i > 1:
                self.grid3.addWidget(QLabel(), 1, i)
                self.grid3.addWidget(QLabel(), 2, i)
        self.grid3.addWidget(QLabel(), 2, 1)
        self.grid3.addWidget(QPushButton("Цемент"), 1, 0)
        self.grid3.addWidget(QPushButton("Добавка"), 2, 0)
        self.grid3.addWidget(QLineEdit(), 1, 1)
        self.grid3.setSpacing(15)
        self.grid3.setColumnStretch(1, 0)
        self.grid3.setColumnMinimumWidth(1, 50)
        self.grid3.setColumnMinimumWidth(3, 50)
        self.grid3.setColumnStretch(2, 1)

        self.buttons.addStretch(1)
        self.calcBtn = QPushButton("Рассчитать")
        self.calcBtn.clicked.connect(self.Calculate)
        self.saveBtn = QPushButton("Сохранить")
        self.saveBtn.clicked.connect(self.Save)
        self.buttons.addWidget(self.calcBtn)
        self.buttons.addWidget(self.saveBtn)

        self.head.addLayout(self.grid1)
        self.head.addLayout(self.grid2)
        self.body.addLayout(self.head)
        self.body.addLayout(self.grid3)
        self.body.addStretch(1)
        self.body.addLayout(self.buttons)

        self.grid1.setContentsMargins(10, 10, 50, 10)
        self.grid3.setContentsMargins(10, 50, 10, 50)

        self.grid3.itemAtPosition(2, 0).widget().setProperty("index", 2)

        self.grid3.itemAtPosition(1, 0).widget().clicked.connect(self.AddCement)
        self.grid3.itemAtPosition(2, 0).widget().clicked.connect(self.AddAdditive)

        self.setLayout(self.body)
    
    def AddCement(self):
        self.calculated = False
        result = 0
        table = ChoiceTable(self.DataBase, "Цемент")
        table.show()
        table.exec_()
        if not isinstance(table.result, list):
            pass
        else:
            self.cementId = table.result[0]
            self.grid3.itemAtPosition(1, 0).widget().setText(table.result[1])
            self.grid3.itemAtPosition(1, 2).widget().setText(str(table.result[2]))

    def AddAdditive(self):
        self.calculated = False
        i = self.sender().property("index")
        result = 0
        table = ChoiceTable(self.DataBase, "Добавка")
        table.show()
        table.exec_()
        if not isinstance(table.result, list):
            pass
        elif table.result[0] in self.additivesIds:
            error = QMessageBox()
            error.setWindowTitle("Ошибка!")
            error.setText("Этот реагент уже добавлен.")
            error.setIcon(QMessageBox.Warning)
            error.exec_()
        else:
            self.additivesIds.append(table.result[0])
            self.grid3.itemAtPosition(i, 1).widget().deleteLater()
            self.grid3.addWidget(QLineEdit(), i, 1)
            self.grid3.itemAtPosition(i, 0).widget().setText(table.result[1])
            self.grid3.itemAtPosition(i, 0).widget().clicked.disconnect()
            self.grid3.itemAtPosition(i, 0).widget().clicked.connect(self.ChangeAdditive)
            self.grid3.itemAtPosition(i, 0).widget().setContextMenuPolicy(Qt.CustomContextMenu)
            self.grid3.itemAtPosition(i, 0).widget().customContextMenuRequested.connect(self.DeleteAdditive)
            self.grid3.itemAtPosition(i, 2).widget().setText(str(table.result[2]))
            for j in range(3, len(self.labels3)):
                self.grid3.itemAtPosition(i, j).widget().setText("")
            self.grid3.addWidget(QPushButton("Добавка"), i + 1, 0)
            for j in range(1, len(self.labels3)):
                self.grid3.addWidget(QLabel(), i + 1, j)
            self.grid3.itemAtPosition(i + 1, 0).widget().clicked.connect(self.AddAdditive)
            self.grid3.itemAtPosition(i + 1, 0).widget().setProperty("index", i + 1)
    
    def ChangeAdditive(self):
        self.calculated = False
        i = self.sender().property("index")
        result = 0
        table = ChoiceTable(self.DataBase, "Добавка")
        table.show()
        table.exec_()
        if not isinstance(table.result, list):
            pass
        elif table.result[0] in self.additivesIds:
            error = QMessageBox()
            error.setWindowTitle("Ошибка!")
            error.setText("Этот реагент уже добавлен.")
            error.setIcon(QMessageBox.Warning)
            error.exec_()
        else:
            self.additivesIds[i - 2] = table.result[0]
            self.grid3.itemAtPosition(i, 0).widget().setText(table.result[1])
            self.grid3.itemAtPosition(i, 2).widget().setText(str(table.result[2]))
            for j in range(3, 8):
                self.grid3.itemAtPosition(i, j).widget().setText("")
    
    def DeleteAdditive(self):
        self.calculated = False
        i = self.sender().property("index")

        for j in reversed(range(self.grid3.columnCount())):
            item = self.grid3.itemAtPosition(i, j)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            self.grid3.removeItem(item)

        for row in range(i + 1, 3 + len(self.additivesIds)):
            for col in range(self.grid3.columnCount()):
                item = self.grid3.itemAtPosition(row, col)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        self.grid3.addWidget(widget, row - 1, col)
        
        self.grid3.itemAtPosition(1 + len(self.additivesIds), 0).widget().setText("Добавка")
        for j in range(1, self.grid3.columnCount()):
            item = self.grid3.itemAtPosition(1 + len(self.additivesIds), j)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            self.grid3.removeItem(item)
            self.grid3.addWidget(QLabel(), 1 + len(self.additivesIds), j)
        
        for j in reversed(range(self.grid3.columnCount())):
            item = self.grid3.itemAtPosition(2 + len(self.additivesIds), j)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            self.grid3.removeItem(item)

        del self.additivesIds[i - 2]

        for j in range(i, 3 + len(self.additivesIds)):
            btn = self.grid3.itemAtPosition(j, 0).widget()
            btn.setProperty("index", j)
        
        self.resize(self.sizeHint())

    def isPossibleToCalculate(self):
        if self.grid1.itemAtPosition(1, 1).widget().text() == "" or self.grid1.itemAtPosition(2, 1).widget().toPlainText() == "" or self.grid1.itemAtPosition(4, 1).widget().text() == "":
            error = QMessageBox()
            error.setWindowTitle("Ошибка!")
            error.setText("Заполнены не все поля.")
            error.setIcon(QMessageBox.Warning)
            error.exec_()
            return False
        elif not isNumber(self.grid1.itemAtPosition(3, 1).widget().text()) or not isNumber(self.grid1.itemAtPosition(5, 1).widget().text()) or not isNumber(self.grid2.itemAtPosition(0, 1).widget().text()) or not isNumber(self.grid2.itemAtPosition(1, 1).widget().text()) or not isNumber(self.grid2.itemAtPosition(2, 1).widget().text()) or not isNumber(self.grid2.itemAtPosition(3, 1).widget().text()) or not isNumber(self.grid2.itemAtPosition(8, 1).widget().text()):
            error = QMessageBox()
            error.setWindowTitle("Ошибка!")
            error.setText("Введены некорректные данные.")
            error.setIcon(QMessageBox.Warning)
            error.exec_()
            return False
        elif self.cementId == -1:
            error = QMessageBox()
            error.setWindowTitle("Ошибка!")
            error.setText("Не выбран цемент.")
            error.setIcon(QMessageBox.Warning)
            error.exec_()
            return False
        elif len(self.additivesIds) < 1:
            error = QMessageBox()
            error.setWindowTitle("Ошибка!")
            error.setText("Не выбраны добавки")
            error.setIcon(QMessageBox.Warning)
            error.exec_()
            return False
        for i in range(1, len(self.additivesIds) + 2):
            if not isNumber(self.grid3.itemAtPosition(i, 1).widget().text()):
                error = QMessageBox()
                error.setWindowTitle("Ошибка!")
                error.setText("Введены некорректные параметры реагентов.")
                error.setIcon(QMessageBox.Warning)
                error.exec_()
                return False
        return True

    def Calculate(self):
        if not self.isPossibleToCalculate():
            return

        self.additionConnections = []
        self.additiveReagents = []

        for i in range(len(self.additivesIds)):
            additiveConnection = Connection(self.id, self.additivesIds[i], float(self.grid3.itemAtPosition(i + 2, 1).widget().text()), False)
            additiveReagent = CompoundReagent(self.DataBase, additiveConnection)
            self.additionConnections.append(additiveConnection)
            self.additiveReagents.append(additiveReagent)
        self.cementConnection = Connection(self.id, self.cementId, float(self.grid3.itemAtPosition(1, 1).widget().text()), True)
        self.cementReagent = CompoundReagent(self.DataBase, self.cementConnection)
        try:
            self.compound = Compound(self.DataBase, self.cementReagent, self.additiveReagents, self.id, self.grid1.itemAtPosition(0, 1).widget().date().toString("dd.MM.yyyy"), self.grid1.itemAtPosition(1, 1).widget().text(), self.grid1.itemAtPosition(2, 1).widget().toPlainText(), float(self.grid1.itemAtPosition(3, 1).widget().text()), self.grid1.itemAtPosition(4, 1).widget().text(), float(self.grid1.itemAtPosition(5, 1).widget().text()), float(self.grid2.itemAtPosition(0, 1).widget().text()), float(self.grid2.itemAtPosition(1, 1).widget().text()), float(self.grid2.itemAtPosition(2, 1).widget().text()), float(self.grid2.itemAtPosition(3, 1).widget().text()), float(self.grid2.itemAtPosition(8, 1).widget().text()))
        except:
            error = QMessageBox()
            error.setWindowTitle("Ошибка!")
            error.setText("Введены некорректные величины, рассчет невозможен")
            error.setIcon(QMessageBox.Warning)
            error.exec_()
            return

        self.grid3.itemAtPosition(1, 3).widget().setText(str(self.compound.cement.k1))
        self.grid3.itemAtPosition(1, 4).widget().setText(str(round(self.compound.cement.m3_mass, 5)))
        self.grid3.itemAtPosition(1, 5).widget().setText(str(round(self.compound.cement.volume, 5)))
        self.grid3.itemAtPosition(1, 6).widget().setText(str(round(self.compound.cement.weight, 5)))
        self.grid3.itemAtPosition(1, 7).widget().setText(str(round(self.compound.cement.additiveVolume, 5)))
        for i in range(len(self.compound.additives)):
            self.grid3.itemAtPosition(i + 2, 3).widget().setText(str(self.compound.additives[i].k1))
            self.grid3.itemAtPosition(i + 2, 4).widget().setText(str(round(self.compound.additives[i].m3_mass, 5)))
            self.grid3.itemAtPosition(i + 2, 5).widget().setText(str(round(self.compound.additives[i].volume, 5)))
            self.grid3.itemAtPosition(i + 2, 6).widget().setText(str(round(self.compound.additives[i].weight, 5)))
            self.grid3.itemAtPosition(i + 2, 7).widget().setText(str(round(self.compound.additives[i].additiveVolume, 5)))
        self.grid3.itemAtPosition(len(self.compound.additives) + 2, 0).widget().setText("Вода")
        self.grid3.itemAtPosition(len(self.compound.additives) + 2, 1).widget().setText(str(round(self.compound.waterPrecent, 5)))
        self.grid3.itemAtPosition(len(self.compound.additives) + 2, 2).widget().setText("1")
        self.grid3.itemAtPosition(len(self.compound.additives) + 2, 4).widget().setText(str(round(self.compound.water_m3_mass, 5)))
        self.grid3.itemAtPosition(len(self.compound.additives) + 2, 5).widget().setText(str(round(self.compound.water_m3_mass / 1000, 5)))
        self.grid3.itemAtPosition(len(self.compound.additives) + 2, 6).widget().setText(str(round(self.compound.waterWeight, 5)))
        self.grid3.itemAtPosition(len(self.compound.additives) + 2, 7).widget().setText(str(round(self.compound.waterWeight, 5)))

        self.grid2.itemAtPosition(0, 1).widget().setText(str(round(self.compound.staticTemp, 5)))
        self.grid2.itemAtPosition(0, 2).widget().setText(str(round(toFarenheit(self.compound.staticTemp), 5)) + " °F")
        self.grid2.itemAtPosition(1, 1).widget().setText(str(round(self.compound.circulationTemp, 5)))
        self.grid2.itemAtPosition(1, 2).widget().setText(str(round(toFarenheit(self.compound.circulationTemp), 5)) + " °F")
        self.grid2.itemAtPosition(2, 1).widget().setText(str(round(self.compound.pressure, 5)))
        self.grid2.itemAtPosition(2, 2).widget().setText(str(round(toMPa(self.compound.pressure), 5)) + " МПа")
        self.grid2.itemAtPosition(3, 1).widget().setText(str(round(self.compound.density, 5)))
        self.grid2.itemAtPosition(3, 2).widget().setText(str(round(toPpg(self.compound.density), 5)) + " ppg")
        self.grid2.itemAtPosition(4, 1).widget().setText(str(round(self.compound.cementExit, 5)) + " м3/т")
        self.grid2.itemAtPosition(4, 2).widget().setText(str(round(toFtsk(self.compound.cementExit), 5)) + " ft3/sk")
        self.grid2.itemAtPosition(5, 1).widget().setText(str(round(self.compound.WCRatio, 5)) + " м3/т")
        self.grid2.itemAtPosition(5, 2).widget().setText(str(round(toGalsk(self.compound.WCRatio), 5)) + " gal/sk")
        self.grid2.itemAtPosition(6, 1).widget().setText(str(round(self.compound.mixtureExit, 5)) + " м3/т")
        self.grid2.itemAtPosition(6, 2).widget().setText(str(round(toFtsk(self.compound.mixtureExit), 5)) + " ft3/sk")
        self.grid2.itemAtPosition(7, 1).widget().setText(str(round(self.compound.WM, 5)) + " м3/т")
        self.grid2.itemAtPosition(7, 2).widget().setText(str(round(toGalsk(self.compound.WM), 5)) + " gal/sk")
        self.grid2.itemAtPosition(9, 1).widget().setText(str(round(self.compound.volume, 5)) + " мл")
        self.calculated = True

    def Save(self):
        if self.calculated:
            connectTable = ConnectionsTable(self.DataBase)
            compoundTable = CompoundsTable(self.DataBase)
            compoundTable.append(self.compound)
            self.cementConnection.compound = self.id
            connectTable.append(self.cementConnection)
            for i in range(len(self.additionConnections)):
                connectTable.append(self.additionConnections[i])
            testTable = TestsTable(self.DataBase)
            testTable.append()
            tw = TestWindow(self.DataBase, 1)
            tw.show()
            self.hide()
            if not self.mainWindow.testTable is None:
                if self.mainWindow.testTable.isVisible():
                    self.mainWindow.testTable.table.UpdateData()
                    self.mainWindow.testTable.table.fill()
                    
        else:
            error = QMessageBox()
            error.setWindowTitle("Ошибка!")
            error.setText("Для сохранения необходимо рассчитать параметры смеси.")
            error.setIcon(QMessageBox.Warning)
            error.exec_()
