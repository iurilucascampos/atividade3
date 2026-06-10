from cliente_modbus import ClienteMODBUS
from interface_kivy import ModbusApp

if __name__ == '__main__':
    cliente = ClienteMODBUS('127.0.0.1', 5020)
    app = ModbusApp(cliente_modbus=cliente)
    app.run()