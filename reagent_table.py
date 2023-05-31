from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QMessageBox
from table import *
from toolsFunctions import isNumber

class VisualReagentsTable(ReagentsTable):
    def __init__(self, DataBase, Window):
        super().__init__(DataBase)
        self.Window = Window

        self.rowsVisible = 20
        self.position = 0
        self.isEnd = False

        self.QTable = QTableWidget()
        self.QTable.setFixedSize(850, 400)

        self.QTable.setColumnCount(7)
        self.QTable.setRowCount(self.rowsVisible)

        self.QTable.setHorizontalHeaderLabels(["Тип", "Название", "Производитель", "Удельный вес", "Первичные свойства", "Вторичные свойства", "Рабочие концентрации", ""]) # заменить на человеческие
        self.QTable.resizeColumnToContents(4)
        self.QTable.resizeColumnToContents(5)
        self.QTable.resizeColumnToContents(6)

        self.data = []; self.UpdateData()
        self.fill()
    
    def UpdateData(self):
        self.cursor.execute(f"select {columnsNames(reagentsColumns[1:])} from Reagents where id > {self.position * self.rowsVisible} and id <= {(self.position + 1) * self.rowsVisible}")
        self.data = self.cursor.fetchall()
        self.isEnd = (self.position + 1) * self.rowsVisible >= self.rowsNumber()
        if self.position == 0:
            self.Window.prevBtn.setEnabled(False)
        else:
            self.Window.prevBtn.setEnabled(True)
        if self.isEnd:
            self.Window.nextBtn.setEnabled(False)
        else:
            self.Window.nextBtn.setEnabled(True)

    def fill(self):
        self.QTable.setRowCount(len(self.data))
        r = [str(i) for i in range(self.position * self.rowsVisible + 1, (self.position + 1) * self.rowsVisible + 1)]
        self.QTable.setVerticalHeaderLabels(r)
        
        for i in range(len(self.data)):
            for j in range(7):
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
    
    def SaveChanges(self):
        for i in range(len(self.data)):
            if not isNumber(self.QTable.item(i, 3).text()):
                error = QMessageBox()
                error.setWindowTitle("Ошибка!")
                error.setText("Введены неккоректные данные в поля, содержащие числовые значения.\nОтмена сохранения.")
                error.setIcon(QMessageBox.Warning)
                error.exec_()
                self.fill()
                return
            if self.QTable.item(i, 0).text() != "Цемент" and self.QTable.item(i, 0).text() != "Добавка":
                error = QMessageBox()
                error.setWindowTitle("Ошибка!")
                error.setText("Введено некорректное значение типа реагента.\nРеагент может быть только цементом или добавкой.\nОтмена сохранения.")
                error.setIcon(QMessageBox.Warning)
                error.exec_()
                self.fill()
                return
    
        for i in range(len(self.data)):
            for j in range(7):
                text = self.QTable.item(i, j).text()
                if j == 3:
                    if self.data[i][j] != float(text):
                        self.cursor.execute(f"update Reagents set {self.columns[j + 1].name} = {float(text)} where id = {self.position * self.rowsVisible + i + 1}")
                else:
                    if self.data[i][j] != self.QTable.item(i, j).text():
                        self.cursor.execute(f"update Reagents set {self.columns[j + 1].name} = '{text}' where id = {self.position * self.rowsVisible + i + 1}")
        self.DataBase.commit()
        self.UpdateData()
        self.fill()

    def DeleteCurrent(self):
        if len(self.data) >= 1:
            self.delete(self.QTable.currentRow() + self.position * self.rowsVisible + 1)
            if len(self.data) <= 1 and self.position > 0:
                self.position -= 1
            self.UpdateData()
            self.fill()

class ReagentsBaseWindow(QWidget):
    def __init__(self, DataBase, mainWindow):
        super().__init__()
        self.setWindowTitle("Таблица реагентов")

        layout = QVBoxLayout()
        buttonsLayout = QHBoxLayout()
        mainButons = QVBoxLayout()
        lrLayout = QHBoxLayout()
        lrLayout.addStretch(1)

        self.mainWindow = mainWindow

        self.saveBtn = QPushButton("Сохранить изменения")
        self.nextBtn = QPushButton(">")
        self.prevBtn = QPushButton("<")
        self.deleteBtn = QPushButton("Удалить")
        self.table = VisualReagentsTable(DataBase, self)

        self.nextBtn.setMaximumWidth(52)
        self.prevBtn.setMaximumWidth(52)
        self.nextBtn.setMinimumHeight(52)
        self.prevBtn.setMinimumHeight(52)
        self.saveBtn.setMinimumWidth(200)
        self.deleteBtn.setMinimumWidth(200)

        self.saveBtn.clicked.connect(self.table.SaveChanges)
        self.nextBtn.clicked.connect(self.table.next)
        self.prevBtn.clicked.connect(self.table.prev)
        self.deleteBtn.clicked.connect(self.table.DeleteCurrent)

        layout.addWidget(self.table.QTable)
        mainButons.addWidget(self.saveBtn)
        mainButons.addWidget(self.deleteBtn)
        lrLayout.addWidget(self.prevBtn)
        lrLayout.addWidget(self.nextBtn)
        buttonsLayout.addLayout(mainButons)
        buttonsLayout.addLayout(lrLayout)
        layout.addLayout(buttonsLayout)

        self.setLayout(layout)
        self.setFixedSize(self.sizeHint())
