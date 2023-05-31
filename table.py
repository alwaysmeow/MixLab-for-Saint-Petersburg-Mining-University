from classes import *
from toolsFunctions import columnsStr, columnsNames
from PyQt5.QtWidgets import QMessageBox
from reagent_delete_dialog import *

class Column:
    def __init__(self, name, type):
        self.name = name
        self.type = type
    def str(self):
        return self.name + ' ' + self.type

class Table:
    def __init__(self, DataBase, name, columns):
        self.DataBase = DataBase
        self.name = name
        self.columns = columns

        self.cursor = DataBase.cursor() # Необходимо закрыть потом
        self.cursor.execute(f"select count(name) from sqlite_master where type = 'table' and name = '{name}'")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute(f"create table {name} ({columnsStr(columns)})")
        
    def rowsNumber(self):
        self.cursor.execute(f"select count(*) from {self.name}")
        return self.cursor.fetchone()[0]

reagentsColumns = [Column("id", "int"), Column("type", "text"), Column("name", "text"), Column("producer", "text"), Column("density", "real"), Column("primaryProperties", "text"), Column("secondaryProperties", "text"), Column("consentrations", "text")]

class ReagentsTable(Table):
    def __init__(self, DataBase):
        super().__init__(DataBase, "Reagents", reagentsColumns)
    
    def append(self, reagent: Reagent):
        self.cursor.execute(f"insert into Reagents ({columnsNames(reagentsColumns)}) values ({self.rowsNumber() + 1}, {reagent.data()})")
        self.DataBase.commit()
    
    def delete(self, index):
        self.cursor.execute(f"select count(*) from Connections where reagent_id = {index}")
        count = self.cursor.fetchone()[0]
        if (count == 0):
            self.cursor.execute(f"delete from Reagents where id = {index}")
            self.cursor.execute(f"update Reagents set id = id - 1 where id > {index}")
            ConnectionsTable(self.DataBase)
            self.cursor.execute(f"update Connections set reagent_id = reagent_id - 1 where reagent_id > {index}")
            self.DataBase.commit()
        else:
            dialog = ReagentDeleteDialog()
            result = dialog.exec_()
            if result == dialog.Accepted:
                self.cursor.execute(f"select compound_id from Connections where reagent_id = {index}")
                compTable = CompoundsTable(self.DataBase)
                for item in self.cursor.fetchall():
                    compTable.delete(item[0])
                self.cursor.execute(f"delete from Reagents where id = {index}")
                self.cursor.execute(f"update Reagents set id = id - 1 where id > {index}")
                ConnectionsTable(self.DataBase)
                self.cursor.execute(f"update Connections set reagent_id = reagent_id - 1 where reagent_id > {index}")
                self.DataBase.commit()

compoundssColumns = [Column("id", "int"), Column("date", "text"), Column("customer", "text"), Column("operationType", "text"), Column("diameter", "int"), Column("solutionType", "text"), Column("heatingTime", "real"), Column("staticTemp", "real"), Column("circulationTemp", "real"), Column("pressure", "real"), Column("density", "real"), Column("mass", "real")]

class CompoundsTable(Table):
    def __init__(self, DataBase):
        super().__init__(DataBase, "Compounds", compoundssColumns)
    
    def append(self, compound: Compound):
        ConnectionsTable(self.DataBase)
        TestsTable(self.DataBase)
        self.cursor.execute(f"update Connections set compound_id = compound_id + 1")
        self.cursor.execute(f"update Tests set id = id + 1")
        self.cursor.execute(f"update Compounds set id = id + 1")
        self.cursor.execute(f"insert into Compounds ({columnsNames(compoundssColumns)}) values (1, {compound.data()})")
        self.DataBase.commit()
    
    def delete(self, index):
        self.cursor.execute(f"delete from Compounds where id = {index}")
        self.cursor.execute(f"update Compounds set id = id - 1 where id > {index}")
        self.DataBase.commit()
        connections = ConnectionsTable(self.DataBase)
        connections.deleteByCompound(index)
        self.cursor.execute(f"update Connections set compound_id = compound_id - 1 where compound_id > {index}")
        tests = TestsTable(self.DataBase)
        tests.delete(index)
    
    def get(self, index):
        self.cursor.execute(f"select * from Compounds where id = {index}")
        return self.cursor.fetchone()

connectionsColumns = [Column("compound_id", "int"), Column("reagent_id", "int"), Column("precent", "real"), Column("is_cement", "boolean")]

class ConnectionsTable(Table):
    def __init__(self, DataBase):
        super().__init__(DataBase, "Connections", connectionsColumns)
    
    def append(self, connection: Connection):
        self.cursor.execute(f"insert into Connections ({columnsNames(connectionsColumns)}) values ({connection.data()})")
        self.DataBase.commit()
    
    def CompoundReagents(self, index):
        connections = []
        self.cursor.execute(f"select * from Connections where compound_id = {index} and is_cement = 1")
        connections.append(Connection(*self.cursor.fetchone()))
        self.cursor.execute(f"select * from Connections where compound_id = {index} and is_cement = 0")
        for data in self.cursor.fetchall():
            connections.append(Connection(*data))
        return connections
    
    def deleteByCompound(self, index):
        self.cursor.execute(f"delete from Connections where compound_id = {index}")
        self.DataBase.commit()

testColumns = [Column("id", "int"),
                Column("density_ppg", "real"), Column("density_gsm", "real"), 
                Column("kneadablility", "int"), Column("kneadTime", "text"), Column("initConsistensy", "int"), Column("vs30", "text"), Column("vs50", "text"), Column("vs70", "text"),
                Column("init_temp", "real"),
                Column("bfc300", "int"), Column("bfc200", "int"), Column("bfc100", "int"), Column("bfc60", "int"), Column("bfc30", "int"), Column("bfc6", "int"), Column("bfc3", "int"),
                Column("bff300", "int"), Column("bff200", "int"), Column("bff100", "int"), Column("bff60", "int"), Column("bff30", "int"), Column("bff6", "int"), Column("bff3", "int"),
                Column("bfsns10s", "int"), Column("bfsns10m", "int"),
                Column("afc300", "int"), Column("afc200", "int"), Column("afc100", "int"), Column("afc60", "int"), Column("afc30", "int"), Column("afc6", "int"), Column("afc3", "int"),
                Column("aff300", "int"), Column("aff200", "int"), Column("aff100", "int"), Column("aff60", "int"), Column("aff30", "int"), Column("aff6", "int"), Column("aff3", "int"),
                Column("afsns10s", "int"), Column("afsns10m", "int"),
                Column("wLml", "int"), Column("wLmin", "int"), Column("fWv", "text"), Column("fW45", "text"),
                Column("usc_temp", "int"),
                Column("ucs50", "text"), Column("ucs500", "text"), Column("ucs1000", "text"), Column("ucs1500", "text"),
                Column("ucs6", "int"), Column("ucs12", "int"), Column("ucs18", "int"), Column("ucs23", "int"),
                Column("csns100", "text"), Column("csns200", "text"), Column("csns300", "text"), Column("csns400", "text"), Column("csns500", "text"),
                Column("comment", "text") 
                ]

class TestsTable(Table):
    def __init__(self, DataBase):
        super().__init__(DataBase, "Tests", testColumns)
    
    def append(self):
        self.cursor.execute(f"insert into Tests (id) values (1)")
        self.DataBase.commit()
    
    def delete(self, index):
        self.cursor.execute(f"delete from Tests where id = {index}")
        self.cursor.execute(f"update Tests set id = id - 1 where id > {index}")
        self.DataBase.commit()
