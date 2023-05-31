class Reagent:
    def __init__(self, type: str, name: str, producer: str, density: float, primaryProperties: str, secondaryProperties: str, consentrations: float):
        self.type = type
        self.name = name
        self.producer = producer
        self.density = density
        self.primaryProperties = primaryProperties
        self.secondaryProperties = secondaryProperties
        self.consentrations = consentrations
    
    def data(self):
        return(f"'{self.type}', '{self.name}', '{self.producer}', {self.density}, '{self.primaryProperties}', '{self.secondaryProperties}', '{self.consentrations}'")

class Connection:
    def __init__(self, compound, reagent, precent, isCement):
        self.compound = compound
        self.reagent = reagent
        self.precent = precent
        self.isCement = isCement
    
    def data(self):
        if self.isCement:
            return(f"{self.compound}, {self.reagent}, {self.precent}, 1")
        else:
            return(f"{self.compound}, {self.reagent}, {self.precent}, 0")

class CompoundReagent:
    def __init__(self, DataBase, connection):
        self.DataBase = DataBase
        cursor = DataBase.cursor()
        
        cursor.execute(f"select name from Reagents where id = {connection.reagent}")
        self.name = cursor.fetchone()[0]

        self.precent = connection.precent

        cursor.execute(f"select density from Reagents where id = {connection.reagent}")
        self.density = cursor.fetchone()[0]

        self.k1 = 0
        self.m3_mass = 0
        self.volume = 0
        self.weight = 0
        self.additiveVolume = 0


class Compound:
    def __init__(self, DataBase, cement, additives, id, date, customer, operationType, diameter, solutionType, heatingTime, staticTemp, circulationTemp, pressure, density, mass):
        self.DataBase = DataBase

        self.id = id
        self.date = date
        self.customer = customer
        self.operationType = operationType
        self.diameter = diameter
        self.solutionType = solutionType
        self.heatingTime = heatingTime

        self.staticTemp = staticTemp
        self.circulationTemp = circulationTemp
        self.pressure = pressure
        self.density = density
        self.mass = mass

        self.cement = cement
        self.additives = additives

        self.cement.k1 = self.cement.precent / (10 ** 5) * (self.cement.density - 1) / (self.cement.density * (self.density - 1))
        k1_summ = self.cement.k1
        for item in self.additives:
            item.k1 = item.precent / (10 ** 5) * (item.density - 1) / (item.density * (self.density - 1))
            k1_summ += item.k1
        
        self.cement.m3_mass = 1 / k1_summ
        m3_mass_summ = self.cement.m3_mass
        for item in self.additives:
            item.m3_mass = self.cement.m3_mass * item.precent / 100
            m3_mass_summ += item.m3_mass

        self.cement.volume = self.cement.m3_mass / self.cement.density / 1000
        volume_summ = self.cement.volume
        for item in self.additives:
            item.volume = item.m3_mass / item.density / 1000
            volume_summ += item.volume
        
        self.water_m3_mass = (1 - volume_summ) * 1000
        self.waterPrecent = self.water_m3_mass / self.cement.m3_mass * 100
        self.waterWeight = self.mass * self.waterPrecent / 100

        self.cement.weight = self.mass
        for item in self.additives:
            item.weight = self.cement.weight * item.precent / 100

        self.cement.additiveVolume = self.cement.weight / self.cement.density
        self.volume = self.cement.additiveVolume
        for item in self.additives:
            item.additiveVolume = item.weight / item.density
            self.volume += item.additiveVolume
        self.volume += self.waterWeight

        self.cementExit = 1000 / self.cement.m3_mass
        self.WCRatio = self.water_m3_mass / self.cement.m3_mass
        self.mixtureExit = 1000 / m3_mass_summ
        self.WM = self.water_m3_mass / m3_mass_summ


    def data(self):
        return(f"'{self.date}', '{self.customer}', '{self.operationType}', {self.diameter}, '{self.solutionType}', {self.heatingTime}, {self.staticTemp}, {self.circulationTemp}, {self.pressure}, {self.density}, {self.mass}")
