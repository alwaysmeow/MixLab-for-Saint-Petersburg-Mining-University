from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QLineEdit, QTextEdit, QMessageBox, QComboBox
from classes import Reagent
from toolsFunctions import isNumber, sameReagentCount

class ReagentForm(QWidget):
    def __init__(self, table, mainWindow):
        super().__init__()

        layout = QVBoxLayout()

        self.table = table
        self.mainWindow = mainWindow
        self.setWindowTitle("Добавить реагент")

        self.typeLabel = QLabel("Вид реагента:")
        self.nameLabel = QLabel("Название:")
        self.producerLabel = QLabel("Производитель:")
        self.densityLabel = QLabel("Удельный вес г/см3:")
        self.primaryPropertiesLabel = QLabel("Первичные свойства:")
        self.secondaryPropertiesLabel = QLabel("Вторичные свойства:")
        self.consentrationsLabel = QLabel("Рабочие концентрации:")

        self.typeBox = QComboBox()

        self.typeBox.addItem("Цемент")
        self.typeBox.addItem("Добавка")

        self.nameBox = QLineEdit()
        self.producerBox = QLineEdit()
        self.densityBox = QLineEdit()
        self.primaryPropertiesBox = QTextEdit()
        self.primaryPropertiesBox.setFixedHeight(50)
        self.secondaryPropertiesBox = QTextEdit()
        self.secondaryPropertiesBox.setFixedHeight(50)
        self.consentrationsBox = QLineEdit()

        self.saveBtn = QPushButton("Сохранить")
        self.saveBtn.clicked.connect(self.save)

        self.cancelBtn = QPushButton("Отмена")
        self.cancelBtn.clicked.connect(self.hide)

        layout.addWidget(self.typeLabel)
        layout.addWidget(self.typeBox)
        layout.addWidget(self.nameLabel)
        layout.addWidget(self.nameBox)
        layout.addWidget(self.producerLabel)
        layout.addWidget(self.producerBox)
        layout.addWidget(self.densityLabel)
        layout.addWidget(self.densityBox)
        layout.addWidget(self.primaryPropertiesLabel)
        layout.addWidget(self.primaryPropertiesBox)
        layout.addWidget(self.secondaryPropertiesLabel)
        layout.addWidget(self.secondaryPropertiesBox)
        layout.addWidget(self.consentrationsLabel)
        layout.addWidget(self.consentrationsBox)
        layout.addWidget(self.saveBtn)
        layout.addWidget(self.cancelBtn)

        self.setLayout(layout)
        self.setFixedSize(self.sizeHint())
    
    def save(self):
        if self.nameBox.text() == "":
            error = QMessageBox()
            error.setWindowTitle("Ошибка!")
            error.setText("Поле названия обязательно к заполнению.")
            error.setIcon(QMessageBox.Warning)
            error.exec_()
        elif sameReagentCount(self.table.DataBase, self.typeBox.currentText(), self.nameBox.text()) > 0:
            error = QMessageBox()
            error.setWindowTitle("Ошибка!")
            error.setText("Реагент с таким же типом и именем уже добавлен в таблицу.")
            error.setIcon(QMessageBox.Warning)
            error.exec_()
        elif not isNumber(self.densityBox.text()):
            error = QMessageBox()
            error.setWindowTitle("Ошибка!")
            error.setText("Удельный вес должен быть записан, как вещественное число.\n(Для разделения дробной части используйте точку)")
            error.setIcon(QMessageBox.Warning)
            error.exec_()
        else:
            item = Reagent(self.typeBox.currentText(), self.nameBox.text(), self.producerBox.text(), self.densityBox.text(), self.primaryPropertiesBox.toPlainText(), self.secondaryPropertiesBox.toPlainText(), self.consentrationsBox.text())
            self.table.append(item)
            if not self.mainWindow.reagentTable is None:
                if self.mainWindow.reagentTable.isVisible():
                    self.mainWindow.reagentTable.table.UpdateData()
                    self.mainWindow.reagentTable.table.fill()
