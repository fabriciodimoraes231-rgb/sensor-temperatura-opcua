#!/usr/bin/env python3
"""
Script de demonstração rápida do sistema de temperatura OPC UA.
Mostra dados do sensor no terminal sem interface gráfica.
"""

import time
import signal
import sys
from servidor_opcua import ServidorOPCUA
from cliente_opcua import ClienteOPCUA
import threading

class DemonstradorRapido:
    """Demonstração rápida do sistema."""
    
    def __init__(self):
        self.servidor = None
        self.cliente = None
        self.executando = False
        
    def parar_sistema(self, signum, frame):
        """Handler para parar o sistema com Ctrl+C."""
        print("\n🛑 Parando sistema...")
        self.executando = False
        
        if self.cliente:
            self.cliente.desconectar()
        
        if self.servidor:
            self.servidor.parar()
        
        print("✅ Sistema parado com sucesso!")
        sys.exit(0)
    
    def mostrar_dados(self):
        """Mostra dados do sensor no terminal."""
        print("\n📊 DADOS DO SENSOR EM TEMPO REAL")
        print("=" * 50)
        
        contador = 0
        while self.executando:
            try:
                stats = self.cliente.obter_estatisticas()
                if stats:
                    contador += 1
                    
                    # Limpar linha anterior (efeito de atualização no lugar)
                    if contador > 1:
                        print("\033[F\033[K", end="")  # Move cursor up e limpa linha
                    
                    # Classificação da temperatura
                    temp = stats['atual']
                    if temp < 18:
                        categoria = "🥶 MUITO FRIO"
                        cor = "\033[96m"  # Ciano
                    elif temp < 20:
                        categoria = "❄️  FRIO"
                        cor = "\033[94m"  # Azul
                    elif temp <= 26:
                        categoria = "😊 CONFORTÁVEL"
                        cor = "\033[92m"  # Verde
                    elif temp <= 30:
                        categoria = "🔥 QUENTE"
                        cor = "\033[93m"  # Amarelo
                    else:
                        categoria = "🌡️  MUITO QUENTE"
                        cor = "\033[91m"  # Vermelho
                    
                    # Mostrar dados com cores
                    print(f"{cor}🌡️  {temp:6.2f}°C {categoria}\033[0m | "
                          f"📈 Média: {stats['media']:5.2f}°C | "
                          f"📊 Min: {stats['minima']:5.2f}°C | "
                          f"📊 Max: {stats['maxima']:5.2f}°C | "
                          f"📋 Leituras: {stats['total_leituras']:3d}")
                
                time.sleep(2)  # Atualizar a cada 2 segundos
                
            except Exception as e:
                print(f"❌ Erro: {e}")
                time.sleep(1)
    
    def executar(self):
        """Executa a demonstração."""
        # Configurar handler para Ctrl+C
        signal.signal(signal.SIGINT, self.parar_sistema)
        
        print("🚀 DEMONSTRAÇÃO DO SISTEMA DE TEMPERATURA OPC UA")
        print("=" * 60)
        print("Este script demonstra o funcionamento do sensor de temperatura")
        print("virtual conectado via protocolo OPC UA.")
        print()
        
        try:
            # 1. Iniciar servidor
            print("1️⃣  Iniciando servidor OPC UA...")
            self.servidor = ServidorOPCUA()
            
            # Iniciar servidor em thread separada
            def iniciar_servidor():
                self.servidor.inicializar_servidor()
                self.servidor.server.start()
                self.servidor.executando = True
                self.servidor.thread_atualizacao = threading.Thread(target=self.servidor.atualizar_valores)
                self.servidor.thread_atualizacao.daemon = True
                self.servidor.thread_atualizacao.start()
            
            thread_servidor = threading.Thread(target=iniciar_servidor)
            thread_servidor.daemon = True
            thread_servidor.start()
            
            print("   ✅ Servidor iniciado!")
            
            # 2. Aguardar servidor estabilizar
            print("2️⃣  Aguardando servidor estabilizar...")
            time.sleep(3)
            print("   ✅ Servidor estável!")
            
            # 3. Conectar cliente
            print("3️⃣  Conectando cliente OPC UA...")
            self.cliente = ClienteOPCUA()
            
            if not self.cliente.conectar():
                raise Exception("Não foi possível conectar ao servidor")
            
            print("   ✅ Cliente conectado!")
            
            # 4. Iniciar coleta de dados
            print("4️⃣  Iniciando coleta de dados...")
            self.cliente.iniciar_leitura_continua()
            time.sleep(2)  # Aguardar primeiros dados
            print("   ✅ Coleta iniciada!")
            
            # 5. Mostrar informações do sistema
            print("\n📋 INFORMAÇÕES DO SISTEMA:")
            print(f"   🌐 Endpoint: opc.tcp://localhost:4840/sensor/temperatura")
            print(f"   🔄 Frequência: 1 leitura/segundo")
            print(f"   📊 Histórico: Últimas 300 leituras")
            print(f"   🌡️  Faixa: 10°C a 40°C")
            print(f"   ⏰ Variação: Ciclo diário simulado")
            
            # 6. Mostrar dados em tempo real
            self.executando = True
            print("\n⏱️  Pressione Ctrl+C para parar")
            time.sleep(1)
            
            self.mostrar_dados()
            
        except Exception as e:
            print(f"❌ Erro na demonstração: {e}")
            self.parar_sistema(None, None)

def main():
    """Função principal."""
    demo = DemonstradorRapido()
    demo.executar()

if __name__ == "__main__":
    main()