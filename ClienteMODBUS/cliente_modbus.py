from pymodbus.client import ModbusTcpClient
import struct 

class ClienteMODBUS:
    def __init__(self, server_ip, porta):
        self._cliente = ModbusTcpClient(host=server_ip, port=porta)

    def conectar(self):
        return self._cliente.connect()

    def desconectar(self):
        self._cliente.close()

    def lerDado(self, tipo, addr):
        if tipo == 1:
            resp = self._cliente.read_holding_registers(address=addr, count=1, device_id=1)
            if resp and not resp.isError():
                return resp.registers[0]
        elif tipo == 2:
            resp = self._cliente.read_coils(address=addr, count=1, device_id=1)
            if resp and not resp.isError():
                return resp.bits[0]
        elif tipo == 3:
            resp = self._cliente.read_input_registers(address=addr, count=1, device_id=1)
            if resp and not resp.isError():
                return resp.registers[0]
        elif tipo == 4:
            resp = self._cliente.read_discrete_inputs(address=addr, count=1, device_id=1)
            if resp and not resp.isError():
                return resp.bits[0]
        return None

    def escreveDado(self, tipo, addr, valor):
        if tipo == 1:
            resp = self._cliente.write_register(address=addr, value=valor, device_id=1)
            return bool(resp and not resp.isError())
        elif tipo == 2:
            resp = self._cliente.write_coil(address=addr, value=bool(valor), device_id=1)
            return bool(resp and not resp.isError())
        return False

    def escrever_float(self, addr, valor):
        packed = struct.pack('>f', float(valor))
        registradores = list(struct.unpack('>HH', packed))
        resp = self._cliente.write_registers(address=addr, values=registradores, device_id=1)
        return bool(resp and not resp.isError())

    def ler_float(self, addr):
        resp = self._cliente.read_holding_registers(address=addr, count=2, device_id=1)
        if resp and not resp.isError():
            packed = struct.pack('>HH', resp.registers[0], resp.registers[1])
            valor = struct.unpack('>f', packed)[0]
            return round(valor, 4)
        return None

    def ler_bits_registrador(self, addr):
        val = self.lerDado(1, addr)
        if val is not None:
            return [bool(val & (1 << i)) for i in range(16)]
        return None

    def escrever_bit_registrador(self, addr, bit_index, bit_valor):
        if not (0 <= bit_index <= 15):
            return False
        val = self.lerDado(1, addr)
        if val is None:
            return False
        if bit_valor:
            val |= (1 << bit_index)
        else:
            val &= ~(1 << bit_index)
        return self.escreveDado(1, addr, val)