#!/usr/bin/env python3
"""
Servidor OPC UA que simula um sensor de temperatura ambiente.
Simula variações realísticas de temperatura com ruído e tendências.
"""

import time
import math
import random
import threading
from datetime import datetime
from opcua import Server, ua

class SensorTemperatura:
    """Classe que simula um sensor de temperatura ambiente realístico."""
    
    def __init__(self):
        self.temperatura_base = 22.0  # Temperatura base em °C
        self.amplitude_diaria = 8.0   # Variação máxima durante o dia
        self.ruido_amplitude = 0.5    # Amplitude do ruído aleatório
        self.tendencia = 0.0          # Tendência de aquecimento/resfriamento
        self.contador_tempo = 0
        
    def obter_temperatura(self):
        """
        Simula leitura do sensor com variação diária e ruído.
        
        Returns:
            float: Temperatura em graus Celsius
        """
        # Incrementa contador para simular passagem do tempo
        self.contador_tempo += 0.1
        
        # Variação cíclica diária (24 horas = 2π)
        ciclo_diario = math.sin(self.contador_tempo * 2 * math.pi / 240) * self.amplitude_diaria
        
        # Ruído aleatório para simular pequenas flutuações
        ruido = random.uniform(-self.ruido_amplitude, self.ruido_amplitude)
        
        # Pequena tendência aleatória
        if random.random() < 0.1:  # 10% de chance de mudança de tendência
            self.tendencia += random.uniform(-0.1, 0.1)
            # Limita a tendência
            self.tendencia = max(-0.5, min(0.5, self.tendencia))
        
        # Calcula temperatura final
        temperatura = self.temperatura_base + ciclo_diario + ruido + self.tendencia
        
        # Garante que a temperatura esteja em uma faixa realística (10°C a 40°C)
        temperatura = max(10.0, min(40.0, temperatura))
        
        return round(temperatura, 2)

class ServidorOPCUA:
    """Servidor OPC UA para disponibilizar dados do sensor de temperatura."""
    
    def __init__(self, endpoint="opc.tcp://localhost:4840/sensor/temperatura"):
        self.endpoint = endpoint
        self.server = None
        self.sensor = SensorTemperatura()
        self.executando = False
        self.thread_atualizacao = None
        
        # Variáveis OPC UA
        self.var_temperatura = None
        self.var_timestamp = None
        self.var_status = None
        self.var_unidade = None
        
    def inicializar_servidor(self):
        """Configura e inicializa o servidor OPC UA."""
        try:
            # Criar servidor
            self.server = Server()
            self.server.set_endpoint(self.endpoint)
            self.server.set_server_name("Servidor Sensor Temperatura")
            
            # Configurar namespace
            uri = "http://sensor.temperatura.opcua"
            idx = self.server.register_namespace(uri)
            
            # Criar objeto para o sensor
            sensor_obj = self.server.nodes.objects.add_object(idx, "SensorTemperatura")
            
            # Criar variáveis do sensor
            self.var_temperatura = sensor_obj.add_variable(
                idx, 
                "Temperatura", 
                0.0,
                varianttype=ua.VariantType.Float
            )
            self.var_temperatura.set_writable(False)
            
            self.var_timestamp = sensor_obj.add_variable(
                idx,
                "Timestamp",
                datetime.now().isoformat(),
                varianttype=ua.VariantType.String
            )
            self.var_timestamp.set_writable(False)
            
            self.var_status = sensor_obj.add_variable(
                idx,
                "Status",
                "Online",
                varianttype=ua.VariantType.String
            )
            self.var_status.set_writable(False)
            
            self.var_unidade = sensor_obj.add_variable(
                idx,
                "Unidade",
                "°C",
                varianttype=ua.VariantType.String
            )
            self.var_unidade.set_writable(False)
            
            # Configurações adicionais do sensor
            config_obj = sensor_obj.add_object(idx, "Configuracao")
            
            var_temp_min = config_obj.add_variable(idx, "TempMinima", 10.0)
            var_temp_min.set_writable(False)
            
            var_temp_max = config_obj.add_variable(idx, "TempMaxima", 40.0)
            var_temp_max.set_writable(False)
            
            var_precisao = config_obj.add_variable(idx, "Precisao", 0.1)
            var_precisao.set_writable(False)
            
            print(f"Servidor OPC UA configurado com endpoint: {self.endpoint}")
            
        except Exception as e:
            print(f"Erro ao configurar servidor: {e}")
            raise
    
    def atualizar_valores(self):
        """Thread que atualiza os valores do sensor continuamente."""
        while self.executando:
            try:
                # Obter nova leitura do sensor
                temperatura = self.sensor.obter_temperatura()
                timestamp = datetime.now()
                
                # Atualizar variáveis OPC UA
                self.var_temperatura.set_value(temperatura)
                self.var_timestamp.set_value(timestamp.isoformat())
                self.var_status.set_value("Online")
                
                # Log da leitura
                print(f"[{timestamp.strftime('%H:%M:%S')}] Temperatura: {temperatura}°C")
                
                # Aguardar próxima leitura (1 segundo)
                time.sleep(1.0)
                
            except Exception as e:
                print(f"Erro ao atualizar valores: {e}")
                self.var_status.set_value("Erro")
                time.sleep(1.0)
    
    def iniciar(self):
        """Inicia o servidor OPC UA."""
        try:
            print("Iniciando servidor OPC UA...")
            
            # Configurar servidor
            self.inicializar_servidor()
            
            # Iniciar servidor
            self.server.start()
            print(f"Servidor iniciado com sucesso em: {self.endpoint}")
            print("Pressione Ctrl+C para parar o servidor")
            
            # Iniciar thread de atualização
            self.executando = True
            self.thread_atualizacao = threading.Thread(target=self.atualizar_valores)
            self.thread_atualizacao.daemon = True
            self.thread_atualizacao.start()
            
            # Manter servidor rodando
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nParando servidor...")
                
        except Exception as e:
            print(f"Erro ao iniciar servidor: {e}")
        finally:
            self.parar()
    
    def parar(self):
        """Para o servidor OPC UA."""
        try:
            self.executando = False
            
            if self.thread_atualizacao and self.thread_atualizacao.is_alive():
                self.thread_atualizacao.join(timeout=2)
            
            if self.server:
                self.server.stop()
                print("Servidor parado com sucesso")
                
        except Exception as e:
            print(f"Erro ao parar servidor: {e}")

def main():
    """Função principal."""
    print("=== Servidor OPC UA - Sensor de Temperatura ===")
    print("Este servidor simula um sensor de temperatura ambiente")
    print("com variações realísticas ao longo do tempo.")
    print()
    
    # Criar e iniciar servidor
    servidor = ServidorOPCUA()
    servidor.iniciar()

if __name__ == "__main__":
    main()