from PyQt5.QtCore import Qt

def isNumber(a):
    try:
        float(a)
        return True
    except:
        return False
    
def toFarenheit(temperature):
    return round(temperature * 9 / 5 + 32, 2)

def toFtsk(value):
    return round(value * 1.5057, 5)

def toPpg(value):
    return round(value * 8.33, 5)

def toMPa(value):
    return round(value * 0.006894757, 5)

def toGalsk(value):
    return round(value * 11.26368, 5)

def columnsStr(columns):
    str = ""
    for i in range(len(columns)):
        str += columns[i].str()
        if i < len(columns) - 1:
            str += ', '
    return str

def columnsNames(columns):
    str = ""
    for i in range(len(columns)):
        str += columns[i].name
        if i < len(columns) - 1:
            str += ', '
    return str

def sameReagentCount(DataBase, type, name):
    cursor = DataBase.cursor()
    cursor.execute(f"select count(name) from Reagents where name = '{name}' and type = '{type}'")
    return cursor.fetchone()[0]

def setInactive(edit):
    edit.setReadOnly(True)
    edit.setStyleSheet("QWidget[readOnly=\"true\"] { background-color: lightgray; }")
    edit.setCursor(Qt.ArrowCursor)
    edit.setFocusPolicy(Qt.NoFocus)