#!/usr/bin/env python3
"""
Cliente OPC UA para ler dados do sensor de temperatura e visualizar em tempo real.
Conecta-se ao servidor OPC UA e coleta dados do sensor de temperatura.
"""

import time
import threading
from datetime import datetime
from collections import deque
from opcua import Client

class ClienteOPCUA:
    """Cliente OPC UA para conectar ao servidor de temperatura."""
    
    def __init__(self, endpoint="opc.tcp://localhost:4840/sensor/temperatura"):
        self.endpoint = endpoint
        self.client = None
        self.conectado = False
        self.executando = False
        
        # Variáveis para armazenar dados
        self.temperaturas = deque(maxlen=300)  # Últimas 300 leituras (5 minutos)
        self.timestamps = deque(maxlen=300)
        self.temperatura_atual = 0.0
        self.status_atual = "Desconectado"
        self.ultima_atualizacao = None
        
        # Referências para as variáveis OPC UA
        self.var_temperatura = None
        self.var_timestamp = None
        self.var_status = None
        self.var_unidade = None
        
        # Thread para leitura contínua
        self.thread_leitura = None
        
    def conectar(self):
        """Conecta ao servidor OPC UA."""
        try:
            print(f"Conectando ao servidor OPC UA em: {self.endpoint}")
            
            # Criar cliente
            self.client = Client(self.endpoint)
            
            # Conectar
            self.client.connect()
            self.conectado = True
            
            print("Conectado com sucesso!")
            
            # Obter referências para as variáveis
            root = self.client.get_root_node()
            sensor_obj = root.get_child(["0:Objects", "2:SensorTemperatura"])
            
            self.var_temperatura = sensor_obj.get_child("2:Temperatura")
            self.var_timestamp = sensor_obj.get_child("2:Timestamp")
            self.var_status = sensor_obj.get_child("2:Status")
            self.var_unidade = sensor_obj.get_child("2:Unidade")
            
            print("Variáveis OPC UA obtidas com sucesso")
            
            return True
            
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            self.conectado = False
            return False
    
    def desconectar(self):
        """Desconecta do servidor OPC UA."""
        try:
            self.executando = False
            
            if self.thread_leitura and self.thread_leitura.is_alive():
                self.thread_leitura.join(timeout=2)
            
            if self.client and self.conectado:
                self.client.disconnect()
                self.conectado = False
                print("Desconectado do servidor OPC UA")
                
        except Exception as e:
            print(f"Erro ao desconectar: {e}")
    
    def ler_dados(self):
        """Lê dados do servidor OPC UA."""
        try:
            if not self.conectado:
                return None
            
            # Ler valores das variáveis
            temperatura = self.var_temperatura.get_value()
            timestamp_str = self.var_timestamp.get_value()
            status = self.var_status.get_value()
            unidade = self.var_unidade.get_value()
            
            # Converter timestamp
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            # Armazenar dados
            self.temperatura_atual = temperatura
            self.status_atual = status
            self.ultima_atualizacao = timestamp
            
            # Adicionar aos históricos
            self.temperaturas.append(temperatura)
            self.timestamps.append(timestamp)
            
            return {
                'temperatura': temperatura,
                'timestamp': timestamp,
                'status': status,
                'unidade': unidade
            }
            
        except Exception as e:
            print(f"Erro ao ler dados: {e}")
            self.status_atual = "Erro de leitura"
            return None
    
    def leitura_continua(self):
        """Thread que realiza leitura contínua dos dados."""
        while self.executando:
            try:
                dados = self.ler_dados()
                if dados:
                    print(f"[{dados['timestamp'].strftime('%H:%M:%S')}] "
                          f"Temperatura: {dados['temperatura']}{dados['unidade']} "
                          f"Status: {dados['status']}")
                
                time.sleep(1.0)  # Leitura a cada segundo
                
            except Exception as e:
                print(f"Erro na leitura contínua: {e}")
                time.sleep(1.0)
    
    def iniciar_leitura_continua(self):
        """Inicia a leitura contínua em thread separada."""
        if not self.conectado:
            print("Erro: Cliente não está conectado")
            return False
        
        self.executando = True
        self.thread_leitura = threading.Thread(target=self.leitura_continua)
        self.thread_leitura.daemon = True
        self.thread_leitura.start()
        
        print("Leitura contínua iniciada")
        return True
    
    def obter_historico(self, limite=100):
        """
        Retorna histórico de temperaturas.
        
        Args:
            limite (int): Número máximo de leituras a retornar
            
        Returns:
            tuple: (temperaturas, timestamps)
        """
        if limite > len(self.temperaturas):
            limite = len(self.temperaturas)
        
        temps = list(self.temperaturas)[-limite:]
        times = list(self.timestamps)[-limite:]
        
        return temps, times
    
    def obter_estatisticas(self):
        """
        Calcula estatísticas dos dados coletados.
        
        Returns:
            dict: Estatísticas (média, min, max, etc.)
        """
        if not self.temperaturas:
            return None
        
        temps = list(self.temperaturas)
        
        return {
            'media': sum(temps) / len(temps),
            'minima': min(temps),
            'maxima': max(temps),
            'atual': self.temperatura_atual,
            'total_leituras': len(temps),
            'status': self.status_atual,
            'ultima_atualizacao': self.ultima_atualizacao
        }

def main():
    """Função principal para testar o cliente OPC UA."""
    print("=== Cliente OPC UA - Sensor de Temperatura ===")
    print("Este cliente conecta ao servidor OPC UA e coleta dados do sensor.")
    print()
    
    # Criar cliente
    cliente = ClienteOPCUA()
    
    try:
        # Conectar ao servidor
        if not cliente.conectar():
            print("Erro: Não foi possível conectar ao servidor")
            print("Certifique-se de que o servidor está rodando")
            return
        
        # Iniciar leitura contínua
        cliente.iniciar_leitura_continua()
        
        # Manter cliente rodando e mostrar estatísticas periodicamente
        print("Cliente iniciado. Pressione Ctrl+C para parar")
        print("=" * 50)
        
        contador = 0
        while True:
            time.sleep(10)  # Mostrar estatísticas a cada 10 segundos
            contador += 1
            
            stats = cliente.obter_estatisticas()
            if stats:
                print(f"\n--- Estatísticas ({contador * 10}s) ---")
                print(f"Temperatura atual: {stats['atual']:.2f}°C")
                print(f"Média: {stats['media']:.2f}°C")
                print(f"Mínima: {stats['minima']:.2f}°C")
                print(f"Máxima: {stats['maxima']:.2f}°C")
                print(f"Total de leituras: {stats['total_leituras']}")
                print(f"Status: {stats['status']}")
                print("-" * 30)
    
    except KeyboardInterrupt:
        print("\nParando cliente...")
    
    except Exception as e:
        print(f"Erro: {e}")
    
    finally:
        cliente.desconectar()

if __name__ == "__main__":
    main()