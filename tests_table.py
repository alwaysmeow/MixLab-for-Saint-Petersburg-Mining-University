from table import CompoundsTable
from PyQt5.QtWidgets import QWidget, QPushButton, QTableWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QAbstractItemView
from test_window import TestWindow

class VisualTestTable(CompoundsTable):
    def __init__(self, DataBase, window):
        super().__init__(DataBase)

        self.window = window
        self.DataBase = DataBase

        self.rowsVisible = 20
        self.position = 0
        self.isEnd = False

        self.QTable = QTableWidget()
        self.QTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.QTable.cellDoubleClicked.connect(self.open)

        self.QTable.setFixedSize(700, 400)
        self.QTable.setColumnCount(5)
        self.QTable.setHorizontalHeaderLabels(["Дата", "Заказчик", "Тип операции", "Диаметр ОК", "Тип раствора"])

        self.data = []; self.UpdateData()
        self.fill()

    def UpdateData(self):
        self.cursor.execute(f"select date, customer, operationType, diameter, solutionType from Compounds where id > {self.position * self.rowsVisible} and id <= {(self.position + 1) * self.rowsVisible} order by id asc")
        self.data = self.cursor.fetchall()
        self.isEnd = (self.position + 1) * self.rowsVisible >= self.rowsNumber()
        if self.position == 0:
            self.window.prevBtn.setEnabled(False)
        else:
            self.window.prevBtn.setEnabled(True)
        if self.isEnd:
            self.window.nextBtn.setEnabled(False)
        else:
            self.window.nextBtn.setEnabled(True)

    def fill(self):
        self.QTable.setRowCount(len(self.data))
        r = [str(i) for i in range(self.position * self.rowsVisible + 1, (self.position + 1) * self.rowsVisible + 1)]
        self.QTable.setVerticalHeaderLabels(r)

        for i in range(len(self.data)):
            for j in range(5):
                self.QTable.setItem(i, j, QTableWidgetItem(str(self.data[i][j])))

    def next(self):
        if not self.isEnd:
            self.position += 1
            self.UpdateData()
            self.fill()

    def prev(self):
        if self.position > 0:
            self.position -= 1
            self.UpdateData()
            self.fill()

    def DeleteCurrent(self):
        if len(self.data) >= 1:
            self.delete(self.QTable.currentRow() + self.position * self.rowsVisible + 1)
            if len(self.data) <= 1 and self.position > 0:
                self.position -= 1
            self.UpdateData()
            self.fill()

    def open(self):
        id = self.QTable.currentRow() + 1 + self.position * self.rowsVisible
        tw = TestWindow(self.DataBase, id)
        tw.show()

class TestsBaseWindow(QWidget):
    def __init__(self, DataBase, mainWindow):
        super().__init__()
        self.setWindowTitle("Таблица лабораторных тестов")

        layout = QVBoxLayout()
        buttonsLayout = QHBoxLayout()

        self.mainWindow = mainWindow

        self.nextBtn = QPushButton(">")
        self.prevBtn = QPushButton("<")
        self.deleteBtn = QPushButton("Удалить")
        self.table = VisualTestTable(DataBase, self)

        self.nextBtn.setMaximumWidth(52)
        self.prevBtn.setMaximumWidth(52)
        self.nextBtn.setMinimumHeight(52)
        self.prevBtn.setMinimumHeight(52)

        self.deleteBtn.clicked.connect(self.table.DeleteCurrent)
        self.prevBtn.clicked.connect(self.table.prev)
        self.nextBtn.clicked.connect(self.table.next)
        
        layout.addWidget(self.table.QTable)
        buttonsLayout.addWidget(self.deleteBtn)
        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(self.prevBtn)
        buttonsLayout.addWidget(self.nextBtn)
        layout.addLayout(buttonsLayout)

        self.setLayout(layout)
        self.setFixedSize(self.sizeHint())
