from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QScrollArea, QTimeEdit
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QFont
from PyQt5.QtCore import QTime, QLocale
from table import *
from classes import *
from toolsFunctions import *
from functools import partial

class TableNumberEdit(QLineEdit):
    def __init__(self, window, column):
        super().__init__()
        self.DataBase = window.DataBase
        self.column = column
        self.id = window.id

        cursor = self.DataBase.cursor()
        cursor.execute(f"select {column} from Tests where id = {self.id}")
        self.value = cursor.fetchone()[0]
        if self.value is None:
            self.setText("")
        else:
            self.setText(str(self.value))

        window.edits.append(self)
    
    def save(self):
        if isNumber(self.text()) and float(self.text()) != self.value:
            cursor = self.DataBase.cursor()
            cursor.execute(f"update Tests set {self.column} = {self.text()} where id = {self.id}")

class TableIntEdit(TableNumberEdit):
    def __init__(self, window, column):
        super().__init__(window, column)
        self.setValidator(QIntValidator())

class TableFloatEdit(TableNumberEdit):
    def __init__(self, window, column):
        super().__init__(window, column)

        locale = QLocale(QLocale.English, QLocale.UnitedStates)
        validator = QDoubleValidator()
        validator.setLocale(locale)

        self.setValidator(validator)

class TableLineEdit(TableNumberEdit):
    def __init__(self, window, column):
        super().__init__(window, column)

    def save(self):
        cursor = self.DataBase.cursor()
        cursor.execute(f"update Tests set {self.column} = '{self.text()}' where id = {self.id}")

class CommentEdit(QTextEdit):
    def __init__(self, window):
        super().__init__()
        self.DataBase = window.DataBase
        self.id = window.id

        cursor = self.DataBase.cursor()
        cursor.execute(f"select comment from Tests where id = {self.id}")
        self.value = cursor.fetchone()[0]
        if self.value is None:
            self.setText("")
        else:
            self.setText(str(self.value))

        window.edits.append(self)

    def save(self):
        cursor = self.DataBase.cursor()
        cursor.execute(f"update Tests set comment = '{self.toPlainText()}' where id = {self.id}")

class TableTimeEdit(QTimeEdit):
    def __init__(self, window, column):
        super().__init__()
        self.DataBase = window.DataBase
        self.column = column
        self.id = window.id

        cursor = self.DataBase.cursor()
        cursor.execute(f"select {column} from Tests where id = {self.id}")
        value = cursor.fetchone()[0]
        if value is None:
            pass
        else:
            self.setTime(QTime.fromString(value, "hh:mm"))

        window.edits.append(self)

    def save(self):
        time = self.time().toString("hh:mm")
        cursor = self.DataBase.cursor()
        cursor.execute(f"update Tests set {self.column} = '{time}' where id = {self.id}")

class Header(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Arial", 12))
        self.setContentsMargins(0, 0, 0, 5)

class TestWindow(QWidget):
    def __init__(self, DataBase, id):
        super().__init__()

        self.DataBase = DataBase
        self.id = id
        self.cursor = self.DataBase.cursor()

        self.connectionsTable = ConnectionsTable(self.DataBase)
        self.compoundsTable = CompoundsTable(self.DataBase)
        self.connections = self.connectionsTable.CompoundReagents(self.id)
        self.reagents = []
        for item in self.connections:
            self.reagents.append(CompoundReagent(self.DataBase, item))
        self.compound = Compound(self.DataBase, self.reagents[0], self.reagents[1:], *self.compoundsTable.get(self.id))
        self.setWindowTitle(f"Тест: {self.compound.date} {self.compound.operationType}")
        
        self.labels1 = ["Дата", "Заказчик", "Тип операции", "Диаметр ОК", "Тип раствора", "Время нагрева, мин"]
        self.labels2 = ["Статическая температура", "Циркуляционная температура", "Давление", "Плотность", "Выход по цементу", "В/Ц", "Выход смеси", "Водосмесевое", "Масса цемента для теста", "Объем готового раствора"]
        self.labels3 = ["Материал", "% от веса цемента", "Удельный вес, г/см^3", "Масса на 1 м3, кг", "Объем", "Вес для теста, гр", "Объем добавок, мл"]

        self.head = QHBoxLayout()
        self.body = QVBoxLayout()
        self.edits = []

        self.grid1 = QGridLayout()
        for i in range(len(self.labels1)):
            self.grid1.addWidget(QLabel(self.labels1[i]), i, 0)
        self.grid1.addWidget(QLabel(self.compound.date), 0, 1)
        self.grid1.addWidget(QLabel(self.compound.customer), 1, 1)
        self.grid1.addWidget(QLabel(self.compound.operationType), 2, 1)
        # Может вылезать за пределы макета
        self.grid1.itemAtPosition(2, 1).widget().setWordWrap(True)
        self.grid1.addWidget(QLabel(str(self.compound.diameter)), 3, 1)
        self.grid1.addWidget(QLabel(self.compound.solutionType), 4, 1)
        self.grid1.addWidget(QLabel(str(self.compound.heatingTime)), 5, 1)
        self.grid1.setRowStretch(6, 1)


        self.grid2 = QGridLayout()
        for i in range(len(self.labels2)):
            self.grid2.addWidget(QLabel(self.labels2[i]), i, 0)
        self.grid2.addWidget(QLabel(str(round(self.compound.staticTemp, 5)) + " °C"), 0, 1)
        self.grid2.addWidget(QLabel(str(round(toFarenheit(self.compound.staticTemp), 5)) + " °F"), 0, 2)
        self.grid2.addWidget(QLabel(str(round(self.compound.circulationTemp, 5)) + " °C"), 1, 1)
        self.grid2.addWidget(QLabel(str(round(toFarenheit(self.compound.circulationTemp), 5)) + " °F"), 1, 2)
        self.grid2.addWidget(QLabel(str(round(self.compound.pressure, 5)) + " psi"), 2, 1)
        self.grid2.addWidget(QLabel(str(round(toMPa(self.compound.circulationTemp), 5)) + " МПа"), 2, 2)
        self.grid2.addWidget(QLabel(str(round(self.compound.density, 5)) + " г/см3"), 3, 1)
        self.grid2.addWidget(QLabel(str(round(toPpg(self.compound.density), 5)) + " ppg"), 3, 2)
        self.grid2.addWidget(QLabel(str(round(self.compound.cementExit, 5)) + " м3/т"), 4, 1)
        self.grid2.addWidget(QLabel(str(round(toFtsk(self.compound.cementExit), 5)) + " ft3/sk"), 4, 2)
        self.grid2.addWidget(QLabel(str(round(self.compound.WCRatio, 5)) + " м3/т"), 5, 1)
        self.grid2.addWidget(QLabel(str(round(toGalsk(self.compound.WCRatio), 5)) + " gal/sk"), 5, 2)
        self.grid2.addWidget(QLabel(str(round(self.compound.mixtureExit, 5)) + " м3/т"), 6, 1)
        self.grid2.addWidget(QLabel(str(round(toFtsk(self.compound.mixtureExit), 5)) + " ft3/sk"), 6, 2)
        self.grid2.addWidget(QLabel(str(round(self.compound.WM, 5)) + " м3/т"), 7, 1)
        self.grid2.addWidget(QLabel(str(round(toGalsk(self.compound.WM), 5)) + " gal/sk"), 7, 2)
        self.grid2.addWidget(QLabel(str(round(self.compound.mass, 5)) + " г"), 8, 1)
        self.grid2.addWidget(QLabel(str(round(self.compound.volume, 5)) + " мл"), 9, 1)

        self.grid3 = QGridLayout()
        for i in range(len(self.labels3)):
            self.grid3.addWidget(QLabel(self.labels3[i]), 0, i)
        
        self.grid3.addWidget(QLabel(self.compound.cement.name), 1, 0)
        self.grid3.addWidget(QLabel(str(round(self.compound.cement.precent, 5))), 1, 1)
        self.grid3.addWidget(QLabel(str(round(self.compound.cement.density, 5))), 1, 2)
        self.grid3.addWidget(QLabel(str(round(self.compound.cement.m3_mass, 5))), 1, 3)
        self.grid3.addWidget(QLabel(str(round(self.compound.cement.volume, 5))), 1, 4)
        self.grid3.addWidget(QLabel(str(round(self.compound.cement.weight, 5))), 1, 5)
        self.grid3.addWidget(QLabel(str(round(self.compound.cement.additiveVolume, 5))), 1, 6)

        r = len(self.compound.additives)

        for i in range(r):
            self.grid3.addWidget(QLabel(self.compound.additives[i].name), i + 2, 0)
            self.grid3.addWidget(QLabel(str(round(self.compound.additives[i].precent, 5))), i + 2, 1)
            self.grid3.addWidget(QLabel(str(round(self.compound.additives[i].density, 5))), i + 2, 2)
            self.grid3.addWidget(QLabel(str(round(self.compound.additives[i].m3_mass, 5))), i + 2, 3)
            self.grid3.addWidget(QLabel(str(round(self.compound.additives[i].volume, 5))), i + 2, 4)
            self.grid3.addWidget(QLabel(str(round(self.compound.additives[i].weight, 5))), i + 2, 5)
            self.grid3.addWidget(QLabel(str(round(self.compound.additives[i].additiveVolume, 5))), i + 2, 6)

        self.grid3.addWidget(QLabel("Вода"), r + 2, 0)
        self.grid3.addWidget(QLabel(str(round(self.compound.waterPrecent, 5))), r + 2, 1)
        self.grid3.addWidget(QLabel("1"), r + 2, 2)
        self.grid3.addWidget(QLabel(str(round(self.compound.water_m3_mass, 5))), r + 2, 3)
        self.grid3.addWidget(QLabel(str(round(self.compound.water_m3_mass / 1000, 5))), r + 2, 4)
        self.grid3.addWidget(QLabel(str(round(self.compound.waterWeight, 5))), r + 2, 5)
        self.grid3.addWidget(QLabel(str(round(self.compound.waterWeight, 5))), r + 2, 6)

        self.grid3.setSpacing(15)
        self.grid3.setColumnStretch(1, 0)
        self.grid3.setColumnMinimumWidth(1, 50)
        self.grid3.setColumnMinimumWidth(3, 50)
        self.grid3.setColumnStretch(2, 1)

        self.head.addLayout(self.grid1)
        self.head.addLayout(self.grid2)
        self.body.addLayout(self.head)
        self.body.addLayout(self.grid3)

        self.body.addWidget(Header("Результаты лабораторного тестирования"))
        self.grid4 = QGridLayout()
        self.grid4.addWidget(QLabel("Плотность, ppg"), 0, 0)
        self.grid4.addWidget(TableFloatEdit(self, "density_ppg"), 0, 1)
        self.grid4.addWidget(QLabel("Плотность, г/см3"), 0, 2)
        self.grid4.addWidget(TableFloatEdit(self, "density_gsm"), 0, 4)
        self.grid4.addWidget(QLabel("Замешиваемость"), 1, 0)
        self.grid4.addWidget(TableIntEdit(self, "kneadablility"), 1, 1)
        self.grid4.addWidget(QLabel("Время замешивания"), 1, 2)
        self.grid4.addWidget(TableLineEdit(self, "kneadTime"), 1, 4)
        self.grid4.setColumnStretch(5, 1)
        self.body.addLayout(self.grid4)

        self.body.addWidget(Header("Время загустевания"))
        self.grid5 = QGridLayout()
        self.grid5.addWidget(QLabel("Начальное ВС"), 0, 0)
        self.grid5.addWidget(TableIntEdit(self, "initConsistensy"), 1, 0)
        self.grid5.setColumnStretch(1, 1)
        self.grid5.addWidget(QLabel("30 ВС"), 0, 2)
        self.grid5.addWidget(TableTimeEdit(self, "vs30"), 1, 2)
        self.grid5.addWidget(QLabel("50 ВС"), 0, 3)
        self.grid5.addWidget(TableTimeEdit(self, "vs50"), 1, 3)
        self.grid5.addWidget(QLabel("70 ВС"), 0, 4)
        self.grid5.addWidget(TableTimeEdit(self, "vs70"), 1, 4)
        self.grid5.setColumnStretch(5, 1)
        self.body.addLayout(self.grid5)

        self.body.addWidget(Header("Реологические параметры"))
        self.grid6 = QGridLayout()
        self.grid6.addWidget(QLabel("До кондиционирования"), 0, 0)

        self.initTempEdit = TableFloatEdit(self, "init_temp")
        self.initTempEdit.setPlaceholderText("Нач. температура")
        initTempCLayout = QHBoxLayout()
        initTempCLayout.addWidget(self.initTempEdit)
        initTempCLayout.addWidget(QLabel("°C"))
        self.grid6.addLayout(initTempCLayout, 1, 0)

        self.initTempF = QLineEdit()
        initTempFLayout = QHBoxLayout()
        initTempFLayout.addWidget(self.initTempF)
        initTempFLayout.addWidget(QLabel("°F"))
        setInactive(self.initTempF)
        self.grid6.addLayout(initTempFLayout, 2, 0)

        self.initTempEdit.textChanged.connect(self.calcInitTempInF)

        self.grid6.addWidget(QLabel("300"), 0, 1)
        self.grid6.addWidget(TableIntEdit(self, "bfc300"), 1, 1)
        self.grid6.addWidget(TableIntEdit(self, "bff300"), 2, 1)
        self.grid6.addWidget(QLabel("200"), 0, 2)
        self.grid6.addWidget(TableIntEdit(self, "bfc200"), 1, 2)
        self.grid6.addWidget(TableIntEdit(self, "bff200"), 2, 2)
        self.grid6.addWidget(QLabel("100"), 0, 3)
        self.grid6.addWidget(TableIntEdit(self, "bfc100"), 1, 3)
        self.grid6.addWidget(TableIntEdit(self, "bff100"), 2, 3)
        self.grid6.addWidget(QLabel("60"), 0, 4)
        self.grid6.addWidget(TableIntEdit(self, "bfc60"), 1, 4)
        self.grid6.addWidget(TableIntEdit(self, "bff60"), 2, 4)
        self.grid6.addWidget(QLabel("30"), 0, 5)
        self.grid6.addWidget(TableIntEdit(self, "bfc30"), 1, 5)
        self.grid6.addWidget(TableIntEdit(self, "bff30"), 2, 5)
        self.grid6.addWidget(QLabel("6"), 0, 6)
        self.grid6.addWidget(TableIntEdit(self, "bfc6"), 1, 6)
        self.grid6.addWidget(TableIntEdit(self, "bff6"), 2, 6)
        self.grid6.addWidget(QLabel("3"), 0, 7)
        self.grid6.addWidget(TableIntEdit(self, "bfc3"), 1, 7)
        self.grid6.addWidget(TableIntEdit(self, "bff3"), 2, 7)
        self.grid6.addWidget(QLabel("среднее"), 3, 0)
        for i in range(1, 8):
            edit = QLineEdit()
            setInactive(edit)
            self.grid6.addWidget(edit, 3, i)
        self.grid6.addWidget(QLabel("СНС"), 4, 0)
        self.grid6.addWidget(QLabel("10 сек"), 4, 1)
        self.grid6.addWidget(TableIntEdit(self, "bfsns10s"), 4, 2)
        self.grid6.addWidget(QLabel("10 мин"), 4, 3)
        self.grid6.addWidget(TableIntEdit(self, "bfsns10m"), 4, 4)
        self.body.addLayout(self.grid6)

        self.grid7 = QGridLayout()
        self.grid7.addWidget(QLabel("После кондиционирования"), 0, 0)
        self.grid7.addWidget(QLabel(str(round(self.compound.circulationTemp)) + " °C"), 1, 0)
        self.grid7.addWidget(QLabel(str(round(toFarenheit(self.compound.circulationTemp))) + " °F"), 2, 0)
        self.grid7.addWidget(QLabel("300"), 0, 1)
        self.grid7.addWidget(TableIntEdit(self, "afc300"), 1, 1)
        self.grid7.addWidget(TableIntEdit(self, "aff300"), 2, 1)
        self.grid7.addWidget(QLabel("200"), 0, 2)
        self.grid7.addWidget(TableIntEdit(self, "afc200"), 1, 2)
        self.grid7.addWidget(TableIntEdit(self, "aff200"), 2, 2)
        self.grid7.addWidget(QLabel("100"), 0, 3)
        self.grid7.addWidget(TableIntEdit(self, "afc100"), 1, 3)
        self.grid7.addWidget(TableIntEdit(self, "aff100"), 2, 3)
        self.grid7.addWidget(QLabel("60"), 0, 4)
        self.grid7.addWidget(TableIntEdit(self, "afc60"), 1, 4)
        self.grid7.addWidget(TableIntEdit(self, "aff60"), 2, 4)
        self.grid7.addWidget(QLabel("30"), 0, 5)
        self.grid7.addWidget(TableIntEdit(self, "afc30"), 1, 5)
        self.grid7.addWidget(TableIntEdit(self, "aff30"), 2, 5)
        self.grid7.addWidget(QLabel("6"), 0, 6)
        self.grid7.addWidget(TableIntEdit(self, "afc6"), 1, 6)
        self.grid7.addWidget(TableIntEdit(self, "aff6"), 2, 6)
        self.grid7.addWidget(QLabel("3"), 0, 7)
        self.grid7.addWidget(TableIntEdit(self, "afc3"), 1, 7)
        self.grid7.addWidget(TableIntEdit(self, "aff3"), 2, 7)
        self.grid7.addWidget(QLabel("среднее"), 3, 0)
        for i in range(1, 8):
            edit = QLineEdit()
            setInactive(edit)
            self.grid7.addWidget(edit, 3, i)
        self.grid7.addWidget(QLabel("СНС"), 4, 0)
        self.grid7.addWidget(QLabel("10 сек"), 4, 1)
        self.grid7.addWidget(TableIntEdit(self, "afsns10s"), 4, 2)
        self.grid7.addWidget(QLabel("10 мин"), 4, 3)
        self.grid7.addWidget(TableIntEdit(self, "afsns10m"), 4, 4)
        self.body.addLayout(self.grid7)

        for grid in [self.grid6, self.grid7]:
            for column in range(1, 8):
                for row in range(1, 3):
                    widget = grid.itemAtPosition(row, column).widget()
                    widget.textChanged.connect(partial(self.calcAverage, grid, column))

        self.waterLayout = QHBoxLayout()
        self.waterLossLayout = QVBoxLayout()
        self.waterLossLayout.addWidget(Header("Водоотдача"))
        self.freeWaterLayout = QVBoxLayout()
        self.freeWaterLayout.addWidget(Header("Свободная вода"))
        self.grid8 = QGridLayout()
        self.grid9 = QGridLayout()
        self.grid8.addWidget(QLabel("мл:"), 0, 0)
        self.grid8.addWidget(TableIntEdit(self, "wLml"), 0, 1)
        self.grid8.addWidget(QLabel("мин:"), 1, 0)
        self.grid8.addWidget(TableIntEdit(self, "wLmin"), 1, 1)
        self.grid8.addWidget(QLabel("Расчет, сс"), 2, 0)
        edit = QLineEdit()
        setInactive(edit)
        self.grid8.addWidget(edit, 2, 1)
        self.grid8.itemAtPosition(0, 1).widget().textChanged.connect(self.calcWaterloss)
        self.grid8.itemAtPosition(1, 1).widget().textChanged.connect(self.calcWaterloss)

        self.grid9.addWidget(QLabel("Вертикально"), 0, 0)
        self.grid9.addWidget(TableIntEdit(self, "fWv"), 0, 1)
        self.grid9.addWidget(QLabel("При 45°"), 1, 0)
        self.grid9.addWidget(TableIntEdit(self, "fW45"), 1, 1)
        self.grid9.setRowStretch(2, 1)
        self.waterLossLayout.addLayout(self.grid8)
        self.freeWaterLayout.addLayout(self.grid9)
        self.waterLayout.addStretch(1)
        self.waterLayout.addLayout(self.waterLossLayout)
        self.waterLayout.addStretch(1)
        self.waterLayout.addLayout(self.freeWaterLayout)
        self.waterLayout.addStretch(1)
        self.body.addLayout(self.waterLayout)

        self.body.addWidget(Header("Ультразвуковая прочность на сжатие"))
        self.grid10 = QGridLayout()

        self.uscTempEdit = TableIntEdit(self, "usc_temp")
        self.uscTempEdit.setPlaceholderText("Температура")
        uscTempCLayout = QHBoxLayout()
        uscTempCLayout.addWidget(self.uscTempEdit)
        uscTempCLayout.addWidget(QLabel("°C"))
        self.grid10.addLayout(uscTempCLayout, 0, 0)


        self.uscTempF = QLineEdit()
        uscTempFLayout = QHBoxLayout()
        uscTempFLayout.addWidget(self.uscTempF)
        uscTempFLayout.addWidget(QLabel("°F"))
        setInactive(self.uscTempF)
        self.grid10.addLayout(uscTempFLayout, 1, 0)

        self.uscTempEdit.textChanged.connect(self.calcUscTempInF)

        self.grid10.addWidget(QLabel("50 psi"), 0, 1)
        self.grid10.addWidget(TableTimeEdit(self, "ucs50"), 0, 2)
        self.grid10.addWidget(QLabel("6:00"), 1, 1)
        self.grid10.addWidget(TableIntEdit(self, "ucs6"), 1, 2)
        self.grid10.addWidget(QLabel("500 psi"), 0, 3)
        self.grid10.addWidget(TableTimeEdit(self, "ucs500"), 0, 4)
        self.grid10.addWidget(QLabel("12:00"), 1, 3)
        self.grid10.addWidget(TableIntEdit(self, "ucs12"), 1, 4)
        self.grid10.addWidget(QLabel("1000 psi"), 0, 5)
        self.grid10.addWidget(TableTimeEdit(self, "ucs1000"), 0, 6)
        self.grid10.addWidget(QLabel("18:00"), 1, 5)
        self.grid10.addWidget(TableIntEdit(self, "ucs18"), 1, 6)
        self.grid10.addWidget(QLabel("1500 psi"), 0, 7)
        self.grid10.addWidget(TableTimeEdit(self, "ucs1500"), 0, 8)
        self.grid10.addWidget(QLabel("23:00"), 1, 7)
        self.grid10.addWidget(TableIntEdit(self, "ucs23"), 1, 8)
        self.body.addLayout(self.grid10)

        self.body.addWidget(Header("Критический СНС при циркуляционной температуре"))
        self.grid11 = QGridLayout()
        self.grid11.addWidget(QLabel("100 lbs/100ft2"), 0, 0)
        self.grid11.addWidget(TableTimeEdit(self, "csns100"), 1, 0)
        self.grid11.addWidget(QLabel("200 lbs/100ft2"), 0, 1)
        self.grid11.addWidget(TableTimeEdit(self, "csns200"), 1, 1)
        self.grid11.addWidget(QLabel("300 lbs/100ft2"), 0, 2)
        self.grid11.addWidget(TableTimeEdit(self, "csns300"), 1, 2)
        self.grid11.addWidget(QLabel("400 lbs/100ft2"), 0, 3)
        self.grid11.addWidget(TableTimeEdit(self, "csns400"), 1, 3)
        self.grid11.addWidget(QLabel("500 lbs/100ft2"), 0, 4)
        self.grid11.addWidget(TableTimeEdit(self, "csns500"), 1, 4)
        self.body.addLayout(self.grid11)

        transferPeriodLayout = QHBoxLayout()
        transferPeriodLayout.addWidget(QLabel("Переходный период"))
        self.transferPeriodEdit = QLineEdit()
        self.grid11.itemAtPosition(1, 0).widget().timeChanged.connect(self.calcTransferPeriod)
        self.grid11.itemAtPosition(1, 4).widget().timeChanged.connect(self.calcTransferPeriod)
        setInactive(self.transferPeriodEdit)
        transferPeriodLayout.addWidget(self.transferPeriodEdit)
        transferPeriodLayout.addStretch(1)
        self.body.addLayout(transferPeriodLayout)

        self.cl = QLabel("Комментарии")
        self.body.addWidget(self.cl)
        self.commentEdit = CommentEdit(self)
        self.commentEdit.setFixedHeight(80)
        self.body.addWidget(self.commentEdit)

        self.body.addStretch(1)

        self.grid1.setContentsMargins(10, 10, 50, 10)
        self.grid3.setContentsMargins(10, 10, 10, 50)
        self.grid4.setContentsMargins(10, 0, 10, 30)
        self.grid5.setContentsMargins(10, 0, 10, 30)
        self.grid6.setContentsMargins(10, 0, 10, 30)
        self.grid7.setContentsMargins(10, 0, 10, 30)
        self.grid8.setContentsMargins(10, 0, 10, 30)
        self.grid9.setContentsMargins(10, 0, 10, 30)
        self.grid10.setContentsMargins(10, 0, 10, 30)
        self.cl.setContentsMargins(0, 10, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.body)
        self.scroll.setWidget(scroll_widget)
        self.scroll.setGeometry(0, 0, self.width(), self.height())
        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.scroll)

        self.btnLayout = QHBoxLayout()
        self.btnLayout.addStretch(1)
        self.saveBtn = QPushButton("Сохранить")
        self.saveBtn.clicked.connect(self.save)
        self.btnLayout.addWidget(self.saveBtn)
        self.btnLayout.setContentsMargins(10, 10, 10, 10)
        self.layout.addLayout(self.btnLayout)
        
        self.setLayout(self.layout)
        self.setFixedSize(900, 600)

        self.calcInitTempInF()
        self.calcUscTempInF()
        self.calcTransferPeriod()
        for grid in [self.grid6, self.grid7]:
            for column in range(1, 8):
                self.calcAverage(grid, column)
        self.calcWaterloss()

    def save(self):
        self.saveBtn.setText("Подождите")
        self.repaint()
        for item in self.edits:
            item.save()
        self.DataBase.commit()
        self.saveBtn.setText("Сохранить")

    def calcInitTempInF(self):
        if isNumber(self.initTempEdit.text()):
            newText = str(round(toFarenheit(float(self.initTempEdit.text())), 5)) + " °F"
            self.initTempF.setText(newText)
        else:
            self.initTempF.setText("")

    def calcUscTempInF(self):
        if isNumber(self.uscTempEdit.text()):
            newText = str(round(toFarenheit(float(self.uscTempEdit.text())), 5)) + " °F"
            self.uscTempF.setText(newText)
        else:
            self.uscTempF.setText("")

    def calcTransferPeriod(self):
        time1 = self.grid11.itemAtPosition(1, 0).widget().time()
        time2 = self.grid11.itemAtPosition(1, 4).widget().time()
        if time2 >= time1:
            time_diff = time1.secsTo(time2)
            time_diff = QTime(0, 0, 0, 0).addSecs(time_diff).toString("hh:mm")
            self.transferPeriodEdit.setText(time_diff)
        else:
            self.transferPeriodEdit.setText("")

    def calcAverage(self, grid, column):
        if isNumber(grid.itemAtPosition(1, column).widget().text()) and isNumber(grid.itemAtPosition(2, column).widget().text()):
            first = int(grid.itemAtPosition(1, column).widget().text())
            second = int(grid.itemAtPosition(2, column).widget().text())
            average = (first + second) / 2
            grid.itemAtPosition(3, column).widget().setText(str(average))
        else:
            grid.itemAtPosition(3, column).widget().setText("")

    def calcWaterloss(self):
        if isNumber(self.grid8.itemAtPosition(0, 1).widget().text()) and isNumber(self.grid8.itemAtPosition(1, 1).widget().text()):
            ml = int(self.grid8.itemAtPosition(0, 1).widget().text())
            min = int(self.grid8.itemAtPosition(1, 1).widget().text())
            waterloss = 2 * ml * (30 / min) ** 0.5
            self.grid8.itemAtPosition(2, 1).widget().setText(str(waterloss))
        else:
            self.grid8.itemAtPosition(2, 1).widget().setText("")
