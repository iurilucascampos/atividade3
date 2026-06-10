import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.textfield import MDTextField

class ModbusInterfaceScreen(MDScreen):
    def __init__(self, cliente_modbus, **kwargs):
        super().__init__(**kwargs)
        self.cliente = cliente_modbus
        self.recv_clock = None
        
        ip_inicial = "127.0.0.1"
        porta_inicial = 5020
        
        # Correção segura: lidando com comm_params como OBJETO, não dicionário
        if hasattr(self.cliente._cliente, 'comm_params'):
            ip_inicial = getattr(self.cliente._cliente.comm_params, 'host', ip_inicial)
            porta_inicial = getattr(self.cliente._cliente.comm_params, 'port', porta_inicial)
        elif hasattr(self.cliente._cliente, 'params'):
            ip_inicial = getattr(self.cliente._cliente.params, 'host', ip_inicial)
            porta_inicial = getattr(self.cliente._cliente.params, 'port', porta_inicial)
        else:
            ip_inicial = getattr(self.cliente._cliente, 'host', ip_inicial)
            porta_inicial = getattr(self.cliente._cliente, 'port', porta_inicial)

        main_layout = MDBoxLayout(orientation='vertical', padding=20, spacing=15)
        
        conn_layout = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=60)
        self.tf_ip = MDTextField(text=str(ip_inicial), hint_text="IP do Servidor")
        self.tf_port = MDTextField(text=str(porta_inicial), hint_text="Porta")
        self.btn_connect = MDRaisedButton(text="Conectar", on_release=self.toggle_connection)
        conn_layout.add_widget(self.tf_ip)
        conn_layout.add_widget(self.tf_port)
        conn_layout.add_widget(self.btn_connect)
        main_layout.add_widget(conn_layout)
        
        data_layout = MDGridLayout(cols=2, spacing=15, size_hint_y=None, height=200)
        self.tf_address = MDTextField(text="0", hint_text="Endereço Modbus")
        self.tf_value = MDTextField(text="", hint_text="Valor / Posição do Bit")
        
        type_box = MDBoxLayout(orientation='horizontal', spacing=5)
        self.cb_coil = MDCheckbox(group='data_type', active=True)
        self.cb_holding = MDCheckbox(group='data_type')
        self.cb_float = MDCheckbox(group='data_type')
        self.cb_bit = MDCheckbox(group='data_type')
        
        type_box.add_widget(self.cb_coil); type_box.add_widget(MDLabel(text="Coil", adaptive_width=True))
        type_box.add_widget(self.cb_holding); type_box.add_widget(MDLabel(text="Holding", adaptive_width=True))
        type_box.add_widget(self.cb_float); type_box.add_widget(MDLabel(text="Float", adaptive_width=True))
        type_box.add_widget(self.cb_bit); type_box.add_widget(MDLabel(text="Bit", adaptive_width=True))
        
        loop_box = MDBoxLayout(orientation='horizontal', spacing=5)
        self.cb_loop = MDCheckbox(active=False, on_release=self.toggle_loop)
        loop_box.add_widget(self.cb_loop)
        loop_box.add_widget(MDLabel(text="Leitura Recorrente (1s)"))
        
        data_layout.add_widget(self.tf_address)
        data_layout.add_widget(self.tf_value)
        data_layout.add_widget(type_box)
        data_layout.add_widget(loop_box)
        main_layout.add_widget(data_layout)
        
        op_layout = MDBoxLayout(orientation='horizontal', spacing=20, size_hint_y=None, height=50)
        self.btn_read = MDRectangleFlatButton(text="Ler Dados", on_release=self.action_read)
        self.btn_write = MDRectangleFlatButton(text="Escrever Dados", on_release=self.action_write)
        op_layout.add_widget(self.btn_read)
        op_layout.add_widget(self.btn_write)
        main_layout.add_widget(op_layout)
        
        self.lbl_monitor = MDLabel(
            text="Status: Desconectado", halign="center", theme_text_color="Secondary", font_style="H5"
        )
        main_layout.add_widget(self.lbl_monitor)
        self.add_widget(main_layout)

    def toggle_connection(self, instance):
        if self.btn_connect.text == "Conectar":
            try:
                novo_ip = self.tf_ip.text
                nova_porta = int(self.tf_port.text)
                
                if hasattr(self.cliente._cliente, 'comm_params'):
                    self.cliente._cliente.comm_params.host = novo_ip
                    self.cliente._cliente.comm_params.port = nova_porta
                elif hasattr(self.cliente._cliente, 'params'):
                    self.cliente._cliente.params.host = novo_ip
                    self.cliente._cliente.params.port = nova_porta
                else:
                    self.cliente._cliente.host = novo_ip
                    self.cliente._cliente.port = nova_porta
                    
                if self.cliente.conectar():
                    self.btn_connect.text = "Desconectar"
                    self.lbl_monitor.text = "Status: Conectado com sucesso!"
                else:
                    self.lbl_monitor.text = "Erro: Falha ao conectar."
            except Exception as e:
                self.lbl_monitor.text = f"Erro: {e}"
        else:
            self.stop_loop()
            self.cliente.desconectar()
            self.btn_connect.text = "Conectar"
            self.lbl_monitor.text = "Status: Desconectado."

    def action_read(self, *args):
        try:
            addr = int(self.tf_address.text)
        except ValueError:
            self.lbl_monitor.text = "Erro: Endereço inválido."
            return

        res = None
        if self.cb_coil.active:
            res = self.cliente.lerDado(2, addr)
        elif self.cb_holding.active:
            res = self.cliente.lerDado(1, addr)
        elif self.cb_float.active:
            res = self.cliente.ler_float(addr)
        elif self.cb_bit.active:
            try:
                bit_pos = int(self.tf_value.text)
                lista_bits = self.cliente.ler_bits_registrador(addr)
                if lista_bits is not None and 0 <= bit_pos <= 15:
                    res = lista_bits[bit_pos]
                else:
                    self.lbl_monitor.text = "Erro: Posição do bit inválida."
                    return
            except ValueError:
                self.lbl_monitor.text = "Digite a posição do bit (0-15) no campo Valor."
                return
                
        self.lbl_monitor.text = f"Leitura: {res}" if res is not None else "Erro ou sem resposta do Servidor."

    def action_write(self, instance):
        try:
            addr = int(self.tf_address.text)
            val_str = self.tf_value.text
        except ValueError:
            self.lbl_monitor.text = "Erro: Endereço inválido."
            return

        success = False
        try:
            if self.cb_coil.active:
                success = self.cliente.escreveDado(2, addr, int(val_str))
            elif self.cb_holding.active:
                success = self.cliente.escreveDado(1, addr, int(val_str))
            elif self.cb_float.active:
                success = self.cliente.escrever_float(addr, float(val_str))
            elif self.cb_bit.active:
                partes = val_str.split(',')
                if len(partes) == 2:
                    success = self.cliente.escrever_bit_registrador(addr, int(partes[0]), int(partes[1]))
                else:
                    self.lbl_monitor.text = "Formato para bit: posicao,valor (Ex: 2,1)"
                    return
        except ValueError:
            self.lbl_monitor.text = "Erro: Verifique o valor inserido."
            return
            
        self.lbl_monitor.text = "Escrita realizada com sucesso!" if success else "Erro ao escrever."

    def toggle_loop(self, checkbox):
        if checkbox.active:
            self.recv_clock = Clock.schedule_interval(self.action_read, 1.0)
        else:
            self.stop_loop()

    def stop_loop(self):
        if self.recv_clock:
            Clock.unschedule(self.recv_clock)
            self.cb_loop.active = False

class ModbusApp(MDApp):
    def __init__(self, cliente_modbus, **kwargs):
        super().__init__(**kwargs)
        self.cliente = cliente_modbus

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        return ModbusInterfaceScreen(cliente_modbus=self.cliente)