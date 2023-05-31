from startwindow import *
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QIcon
import os, sys
from table import *
import sqlite3 as sql
os.getcwd()

if __name__ == "__main__":
    DataBase = sql.connect("DataBase.db")

    ReagentsTable(DataBase)
    CompoundsTable(DataBase)
    ConnectionsTable(DataBase)
    TestsTable(DataBase)
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = StartWindow(DataBase)

    window.show()
    sys.exit(app.exec_())
