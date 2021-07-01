from __future__ import annotations
from abc import ABC, abstractmethod
import re
import json

class DSMR_Parser(object):
    """
    P1 datagram parser for Dutch Smart Meter Readings
    """
    def __init__(self, datagram) -> None:
        self._strategy = DSMR_UNKNOWN()
        self._datagram = datagram
        if re.search(r'1-3:0\.2\.8\(42\)', self._datagram) != None:
            self._strategy = DSMR_41()
        elif re.search(r'1-3:0\.2\.8\(50\)', self._datagram) != None:
            self._strategy = DSMR_50()
        elif re.search(r'0-0:96\.1\.1(\(([a-zA-Z0-9]{1,96})\))', self._datagram).group(2) != "":
            self._strategy = DSMR_3()
        elif re.search(r'0-0:42\.0\.0(\(([a-zA-Z0-9]{1,96})\))', self._datagram).group(2) != "":
            self._strategy = DSMR_22()

    @property
    def strategy(self) -> Strategy:
        return self._strategy

    # @property
    # def datagram(self) :
    #     return self._datagram

    @strategy.setter
    def strategy(self, strategy: Strategy) -> None:
        self._strategy = strategy

    # @datagram.setter
    # def datagram(self, datagram):
    #     self._datagram = datagram

    def parse(self) -> ():
        return self._strategy.parse(self._datagram)

def SafeSearch(pattern, datagram):
    result = re.search(pattern, datagram)
    value = 'NAN'
    if result != None:
        value = result.group(1)
    return value

def SafeUnitSearch(pattern, datagram):
    result = re.search(pattern, datagram)
    value = ('NAN', 'NAN')
    if result != None:
        value = result.group(1,2)
    return value

def SafeConversionInteger(value):
    if value == 'NAN':
        return value
    else:
        return int(value)

def SafeConversionFloat(value):
    if value == 'NAN':
        return value
    else:
        return float(value)

class Strategy(ABC):
    @abstractmethod
    def parse(self, datagram):
        pass

class DSMR_UNKNOWN(Strategy):
    def parse(self, datagram):
        return {}

class DSMR_22(Strategy):
    def parse(self, datagram):
        #print("entered dsmr 22")
        data = Data()
        # info
        data.version = "22"
        
        # Manufacturer
        data.manufacturer = re.search(r'([a-zA-Z]{3}[0-9]([\\]*)([0-9a-zA-Z .-]+))', datagram).group(1)

        # Power DELIVERED by client
        data.power_delivered = "NAN"

        # Power RECEIVED by client
        data.power_received = re.search(r'1-0:1\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram).group(1,2)

        # Energy DELIVERED tariff 1 TO client
        data.energy_to_t1 = re.search(r'1-0:1\.8\.1\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)
        data.energy_to_t2 = re.search(r'1-0:1\.8\.2\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)

        # Energy DELIVERED tariff 2 BY client
        data.energy_by_t1 = re.search(r'1-0:2\.8\.1\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)
        data.energy_by_t2 = re.search(r'1-0:2\.8\.2\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)

        # Current TARIFF
        data.tariff = re.search(r'0-0:96\.14\.0\(([0-9]*)\)', datagram).group(1)

        # Equipment ID
        data.equipment_id = re.search(r'0-0:42\.0\.0(\(([a-zA-Z0-9]{1,96})\))', datagram).group(2)

        # Bundle all in dictionary
        return data.ToJSON()

class DSMR_3(Strategy):
    def parse(self, datagram):
        #print("entered dsmr 3")
        data = Data()
        # info
        data.version = "30"

        # Manufacturer
        data.manufacturer = re.search(r'([a-zA-Z]{3}[0-9]([\\]*)([0-9a-zA-Z .-]+))', datagram).group(1)

        # Power DELIVERED by client
        data.power_delivered = re.search(r'1-0:1\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram).group(1,2)

        # Power RECEIVED by client
        data.power_received = re.search(r'1-0:2\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram).group(1,2)

        # Energy DELIVERED tariff 1 TO client
        data.energy_to_t1 = re.search(r'1-0:1\.8\.1\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)
        data.energy_to_t2 = re.search(r'1-0:1\.8\.2\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)

        # Energy DELIVERED tariff 2 BY client
        data.energy_by_t1 = re.search(r'1-0:2\.8\.1\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)
        data.energy_by_t2 = re.search(r'1-0:2\.8\.2\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)

        # Current TARIFF
        data.tariff = re.search(r'0-0:96\.14\.0\(([0-9]*)\)', datagram).group(1)

        # Equipment ID
        data.equipment_id = re.search(r'0-0:96\.1\.1(\(([a-zA-Z0-9]{1,96})\))', datagram).group(2)

        # Bundle all in dictionary
        return data.ToJSON()

class DSMR_41(Strategy):
    def parse(self, datagram):
        #print("entered dsmr 42")
        data = Data()
        # info
        data.version = re.search(r'1-3:0\.2\.8\(([0-9]+)\)', datagram).group(1)

        # Manufacturer
        data.manufacturer = re.search(r'([a-zA-Z]{3}[0-9]([\\]*)([0-9a-zA-Z .-]+))', datagram).group(1)

        # Power DELIVERED by client
        data.power_delivered = re.search(r'1-0:1\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram).group(1,2)

        # Power RECEIVED by client
        data.power_received = re.search(r'1-0:2\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram).group(1,2)

        # Energy DELIVERED tariff 1 TO client
        data.energy_to_t1 = re.search(r'1-0:1\.8\.1\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)
        data.energy_to_t2 = re.search(r'1-0:1\.8\.2\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)

        # Energy DELIVERED tariff 2 BY client
        data.energy_by_t1 = re.search(r'1-0:2\.8\.1\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)
        data.energy_by_t2 = re.search(r'1-0:2\.8\.2\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)

        # Current TARIFF
        data.tariff = re.search(r'0-0:96\.14\.0\(([0-9]*)\)', datagram).group(1)

        # Equipment ID
        data.equipment_id = re.search(r'0-0:96\.1\.1(\(([a-zA-Z0-9]{1,96})\))', datagram).group(2)

        # Number of power failures in phases
        data.power_failures = SafeSearch(r'0-0:96\.7\.21\(([0-9]*)\)', datagram)

        # Number long power failures in phases
        data.long_power_failures = SafeSearch(r'0-0:96\.7\.9\(([0-9]*)\)', datagram)

        # Number of voltage sags in phase L1
        data.voltage_sags_L1 = SafeSearch(r'1-0:32\.32\.0\(([0-9]*)\)', datagram)

        # Number of voltage sags in phase L2
        data.voltage_sags_L2 = SafeSearch(r'1-0:52\.32\.0\(([0-9]*)\)', datagram)

        # Number of voltage sags in phase L3
        data.voltage_sags_L3 = SafeSearch(r'1-0:72\.32\.0\(([0-9]*)\)', datagram)

        # Number of voltage swells in phase L1 
        data.voltage_swells_L1 = SafeSearch(r'1-0:32\.36\.0\(([0-9]*)\)', datagram)

        # Number of voltage swells in phase L2
        data.voltage_swells_L2 = SafeSearch(r'1-0:52\.36\.0\(([0-9]*)\)', datagram)

        # Number of voltage swells in phase L3
        data.voltage_swells_L3 = SafeSearch(r'1-0:72\.36\.0\(([0-9]*)\)', datagram)

        # Instantaneous current L1
        data.instantaneous_current_L1 = SafeUnitSearch(r'1-0:31\.7\.0\(([0-9]*)\*(A)\)', datagram)

        # Instantaneous current L2
        data.instantaneous_current_L2 = SafeUnitSearch(r'1-0:51\.7\.0\(([0-9]*)\*(A)\)', datagram)

        # Instantaneous current L3
        data.instantaneous_current_L3 = SafeUnitSearch(r'1-0:71\.7\.0\(([0-9]*)\*(A)\)', datagram)

        # Instantaneous active power L1 +P
        data.instantaneous_active_power_L1_positive = SafeUnitSearch(r'1-0:21\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram)

        # Instantaneous active power L2 +P
        data.instantaneous_active_power_L2_positive = SafeUnitSearch(r'1-0:41\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram)

        # Instantaneous active power L3 +P
        data.instantaneous_active_power_L3_positive = SafeUnitSearch(r'1-0:41\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram)

        # Instantaneous active power L1 -P
        data.instantaneous_active_power_L1_negative = SafeUnitSearch(r'1-0:22\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram)  

        # Instantaneous active power L2 -P
        data.instantaneous_active_power_L2_negative = SafeUnitSearch(r'1-0:42\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram)  

        # Instantaneous active power L3 -P
        data.instantaneous_active_power_L3_negative = SafeUnitSearch(r'1-0:62\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram)
        # Bundle all in dictionary
        return data.ToJSON()

class DSMR_50(Strategy):
    def parse(self, datagram):
        #print("entered dsmr 5")
        data = Data()
        # info
        data.version = re.search(r'1-3:0\.2\.8\(([0-9]+)\)', datagram).group(1)

        # Manufacturer
        data.manufacturer = re.search(r'([a-zA-Z]{3}[0-9]([\\]*)([0-9a-zA-Z .-]+))', datagram).group(1)
        
        # Power DELIVERED by client
        data.power_delivered = re.search(r'1-0:1\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram).group(1,2)

        # Power RECEIVED by client
        data.power_received = re.search(r'1-0:2\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram).group(1,2)

        # Energy DELIVERED tariff 1 TO client
        data.energy_to_t1 = re.search(r'1-0:1\.8\.1\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)
        data.energy_to_t2 = re.search(r'1-0:1\.8\.2\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)

        # Energy DELIVERED tariff 2 BY client
        data.energy_by_t1 = re.search(r'1-0:2\.8\.1\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)
        data.energy_by_t2 = re.search(r'1-0:2\.8\.2\(0*([0-9]*\.[0-9]*)\*(kWh)\)', datagram).group(1,2)

        # Current TARIFF
        data.tariff = re.search(r'0-0:96\.14\.0\(([0-9]*)\)', datagram).group(1)

        # Equipment ID
        data.equipment_id = re.search(r'0-0:96\.1\.1(\(([a-zA-Z0-9]{1,96})\))', datagram).group(2)

        # Number of power failures in phases
        data.power_failures = SafeSearch(r'0-0:96\.7\.21\(([0-9]*)\)', datagram)

        # Number long power failures in phases
        data.long_power_failures = SafeSearch(r'0-0:96\.7\.9\(([0-9]*)\)', datagram)

        # Number of voltage sags in phase L1
        data.voltage_sags_L1 = SafeSearch(r'1-0:32\.32\.0\(([0-9]*)\)', datagram)

        # Number of voltage sags in phase L2
        data.voltage_sags_L2 = SafeSearch(r'1-0:52\.32\.0\(([0-9]*)\)', datagram)

        # Number of voltage sags in phase L3
        data.voltage_sags_L3 = SafeSearch(r'1-0:72\.32\.0\(([0-9]*)\)', datagram)

        # Number of voltage swells in phase L1 
        data.voltage_swells_L1 = SafeSearch(r'1-0:32\.36\.0\(([0-9]*)\)', datagram)

        # Number of voltage swells in phase L2
        data.voltage_swells_L2 = SafeSearch(r'1-0:52\.36\.0\(([0-9]*)\)', datagram)

        # Number of voltage swells in phase L3
        data.voltage_swells_L3 = SafeSearch(r'1-0:72\.36\.0\(([0-9]*)\)', datagram)

        # Instantaneous voltage L1
        data.instantaneous_voltage_L1 = SafeUnitSearch(r'1-0:32\.7\.0\(([0-9]*\.[0-9]*)\*(V)\)', datagram)

        # Instantaneous voltage L2
        data.instantaneous_voltage_L2 = SafeUnitSearch(r'1-0:52\.7\.0\(([0-9]*\.[0-9]*)\*(V)\)', datagram)

        # Instantaneous voltage L3
        data.instantaneous_voltage_L3 = SafeUnitSearch(r'1-0:72\.7\.0\(([0-9]*\.[0-9]*)\*(V)\)', datagram)

        # Instantaneous current L1
        data.instantaneous_current_L1 = SafeUnitSearch(r'1-0:31\.7\.0\(([0-9]*)\*(A)\)', datagram)

        # Instantaneous current L2
        data.instantaneous_current_L2 = SafeUnitSearch(r'1-0:51\.7\.0\(([0-9]*)\*(A)\)', datagram)

        # Instantaneous current L3
        data.instantaneous_current_L3 = SafeUnitSearch(r'1-0:71\.7\.0\(([0-9]*)\*(A)\)', datagram)

        # Instantaneous active power L1 +P
        data.instantaneous_active_power_L1_positive = SafeUnitSearch(r'1-0:21\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram)

        # Instantaneous active power L2 +P
        data.instantaneous_active_power_L2_positive = SafeUnitSearch(r'1-0:41\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram)

        # Instantaneous active power L3 +P
        data.instantaneous_active_power_L3_positive = SafeUnitSearch(r'1-0:41\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram)

        # Instantaneous active power L1 -P
        data.instantaneous_active_power_L1_negative = SafeUnitSearch(r'1-0:22\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram)  

        # Instantaneous active power L2 -P
        data.instantaneous_active_power_L2_negative = SafeUnitSearch(r'1-0:42\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram)  

        # Instantaneous active power L3 -P
        data.instantaneous_active_power_L3_negative = SafeUnitSearch(r'1-0:62\.7\.0\(([0-9]*\.[0-9]*)\*(kW)\)', datagram)  

        # Bundle all in dictionary
        return data.ToJSON()

class Data(object):
    version = 'NAN'
    manufacturer = 'NAN'
    equipment_id = 'NAN'
    tariff = 'NAN'
    power_delivered = ('NAN','NAN')
    power_received = ('NAN','NAN')
    energy_by_t1 = ('NAN','NAN')
    energy_by_t2 = ('NAN','NAN')
    energy_to_t1 = ('NAN','NAN')
    energy_to_t2 = ('NAN','NAN')
    power_failures = 'NAN'
    long_power_failures = 'NAN'
    voltage_sags_L1 = 'NAN'
    voltage_swells_L1 = 'NAN'
    instantaneous_voltage_L1 = ('NAN','NAN')
    instantaneous_current_L1 = ('NAN','NAN')
    instantaneous_active_power_L1_positive = ('NAN','NAN')
    instantaneous_active_power_L1_negative = ('NAN','NAN')
    voltage_sags_L2 = 'NAN'
    voltage_swells_L2 = 'NAN'
    instantaneous_voltage_L2 = ('NAN','NAN')
    instantaneous_current_L2 = ('NAN','NAN')
    instantaneous_active_power_L2_positive = ('NAN','NAN')
    instantaneous_active_power_L2_negative = ('NAN','NAN')
    voltage_sags_L3 = 'NAN'
    voltage_swells_L3 = 'NAN'
    instantaneous_voltage_L3 = ('NAN','NAN')
    instantaneous_current_L3 = ('NAN','NAN')
    instantaneous_active_power_L3_positive = ('NAN','NAN')
    instantaneous_active_power_L3_negative = ('NAN','NAN')

    def ToJSON(self):
        return {
            'manufacturer': self.manufacturer,
            'version' : self.version,
            'equipment_id': self.equipment_id,
            'tariff': SafeConversionInteger(self.tariff),
            'power' : [
                {'delivered' : {'value': SafeConversionFloat(self.power_delivered[0]), 'unit': self.power_delivered[1] }},
                {'received': {'value': SafeConversionFloat(self.power_received[0]), 'unit': self.power_received[1] }}
            ],
            'energy': [
                {'tariff' : 1,
                    'delivered': {'value': SafeConversionFloat(self.energy_to_t1[0]), 'unit': self.energy_to_t1[1]},
                    'received': {'value': SafeConversionFloat(self.energy_by_t1[0]), 'unit': self.energy_by_t1[1]}
                },
                {'tariff' : 2,
                    'delivered': {'value': SafeConversionFloat(self.energy_to_t2[0]), 'unit': self.energy_to_t2[1]},
                    'received': {'value': SafeConversionFloat(self.energy_by_t2[0]), 'unit': self.energy_by_t2[1]}
                },
            ],
            'phases':{
                'failures' : SafeConversionInteger(self.power_failures),
                'long failures' : SafeConversionInteger(self.long_power_failures),
                'phases' : [
                    {'phase' : 'L1',
                        'sags': SafeConversionInteger(self.voltage_sags_L1),
                        'swells': SafeConversionInteger(self.voltage_swells_L1),
                        'instantaneous voltage': {'value': SafeConversionFloat(self.instantaneous_voltage_L1[0]), 'unit': self.instantaneous_voltage_L1[1]},
                        'instantaneous current': {'value': SafeConversionFloat(self.instantaneous_current_L1[0]), 'unit': self.instantaneous_current_L1[1]},
                        'instantaneous power +P': {'value': SafeConversionFloat(self.instantaneous_active_power_L1_positive[0]), 'unit': self.instantaneous_active_power_L1_positive[1]},
                        'instantaneous power -P': {'value': SafeConversionFloat(self.instantaneous_active_power_L1_negative[0]), 'unit': self.instantaneous_active_power_L1_negative[1]}
                    },
                    {'phase' : 'L2',
                        'sags': SafeConversionInteger(self.voltage_sags_L2),
                        'swells': SafeConversionInteger(self.voltage_swells_L2),
                        'instantaneous voltage': {'value': SafeConversionFloat(self.instantaneous_voltage_L2[0]), 'unit': self.instantaneous_voltage_L2[1]},
                        'instantaneous current': {'value': SafeConversionFloat(self.instantaneous_current_L2[0]), 'unit': self.instantaneous_current_L2[1]},
                        'instantaneous power +P': {'value': SafeConversionFloat(self.instantaneous_active_power_L2_positive[0]), 'unit': self.instantaneous_active_power_L2_positive[1]},
                        'instantaneous power -P': {'value': SafeConversionFloat(self.instantaneous_active_power_L2_negative[0]), 'unit': self.instantaneous_active_power_L2_negative[1]}
                    },
                    {'phase' : 'L3',
                        'sags': SafeConversionInteger(self.voltage_sags_L3),
                        'swells': SafeConversionInteger(self.voltage_swells_L3),
                        'instantaneous voltage': {'value': SafeConversionFloat(self.instantaneous_voltage_L3[0]), 'unit': self.instantaneous_voltage_L3[1]},
                        'instantaneous current': {'value': SafeConversionFloat(self.instantaneous_current_L3[0]), 'unit': self.instantaneous_current_L3[1]},
                        'instantaneous power +P': {'value': SafeConversionFloat(self.instantaneous_active_power_L3_positive[0]), 'unit': self.instantaneous_active_power_L3_positive[1]},
                        'instantaneous power -P': {'value': SafeConversionFloat(self.instantaneous_active_power_L3_negative[0]), 'unit': self.instantaneous_active_power_L3_negative[1]}
                    }
                ]
            }
        }
    

# if __name__ == '__main__':
#     datagram = "/KFM5KAIFA-METER\r\n\r\n1-3:0.2.8(42)\r\n0-0:1.0.0(200213170457W)\r\n0-0:96.1.1(4530303236303030303333333338343136)\r\n1-0:1.8.1(015001.164*kWh)\r\n1-0:1.8.2(012236.435*kWh)\r\n1-0:2.8.1(000942.859*kWh)\r\n1-0:2.8.2(002395.253*kWh)\r\n0-0:96.14.0(0002)\r\n1-0:1.7.0(00.299*kW)\r\n1-0:2.7.0(00.000*kW)\r\n0-0:96.7.21(00001)\r\n0-0:96.7.9(00001)\r\n1-0:99.97.0(2)(0-0:96.7.19)(180712201124S)(0000004179*s)(000101000006W)(2147483647*s)\r\n1-0:32.32.0(00000)\r\n1-0:52.32.0(00000)\r\n1-0:72.32.0(00000)\r\n1-0:32.36.0(00000)\r\n1-0:52.36.0(00000)\r\n1-0:72.36.0(00000)\r\n0-0:96.13.1()\r\n0-0:96.13.0()\r\n1-0:31.7.0(000*A)\r\n1-0:51.7.0(000*A)\r\n1-0:71.7.0(001*A)\r\n1-0:21.7.0(00.101*kW)\r\n1-0:41.7.0(00.038*kW)\r\n1-0:61.7.0(00.158*kW)\r\n1-0:22.7.0(00.000*kW)\r\n1-0:42.7.0(00.000*kW)\r\n1-0:62.7.0(00.000*kW)\r\n0-1:24.1.0(003)\r\n0-1:96.1.0(4730303332353631323831363736343136)\r\n0-1:24.2.1(200213170000W)(06136.485*m3)\r\n!2236\r\n"
#     for x in range(1):
#         parsed = DSMR_Parser(datagram).parse()
#         jsonStr = json.dumps( parsed)
#         print(jsonStr)


