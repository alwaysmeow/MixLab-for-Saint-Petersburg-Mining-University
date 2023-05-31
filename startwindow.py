from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from reagent_form import *
from reagent_table import *
from compound_form import *
from table import *
from test_window import Header
from tests_table import *

class StartWindow(QMainWindow):
    def __init__(self, DataBase):
        super(StartWindow, self).__init__()

        self.DataBase = DataBase

        self.setWindowTitle("MixLab")
        self.setFixedSize(350, 350)

        self.testTable = None
        self.reagentTable = None

        centralWidget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.addWidget(Header("MixLab"))
        self.setCentralWidget(centralWidget)

        self.reagentsBaseBtn = QPushButton(self)
        self.reagentsBaseBtn.setText("База данных реагентов")
        self.reagentsBaseBtn.setFixedWidth(200)
        self.layout.addWidget(self.reagentsBaseBtn)

        self.reagentFormBtn = QPushButton(self)
        self.reagentFormBtn.setText("Добавить реагент")
        self.reagentFormBtn.setFixedWidth(200)
        self.layout.addWidget(self.reagentFormBtn)

        self.testBtn = QPushButton(self)
        self.testBtn.setText("Блок тестирования")
        self.testBtn.setFixedWidth(200)
        self.layout.addWidget(self.testBtn)

        self.testsBaseBtn = QPushButton(self)
        self.testsBaseBtn.setText("База данных тестов")
        self.testsBaseBtn.setFixedWidth(200)
        self.layout.addWidget(self.testsBaseBtn)

        self.reagentFormBtn.clicked.connect(self.OpenReagentForm)
        self.reagentsBaseBtn.clicked.connect(self.OpenReagentsBase)
        self.testBtn.clicked.connect(self.OpenTestForm)
        self.testsBaseBtn.clicked.connect(self.OpenTestTable)

        centralWidget.setLayout(self.layout)

    def OpenReagentForm(self):
        self.reagentForm = ReagentForm(ReagentsTable(self.DataBase), self)
        self.reagentForm.show()
    
    def OpenReagentsBase(self):
        self.reagentTable = ReagentsBaseWindow(self.DataBase, self)
        self.reagentTable.show()
    
    def OpenTestForm(self):
        self.testForm = CompoundForm(self.DataBase, self)
        self.testForm.show()
    
    def OpenTestTable(self):
        self.testTable = TestsBaseWindow(self.DataBase, self)
        self.testTable.show()
