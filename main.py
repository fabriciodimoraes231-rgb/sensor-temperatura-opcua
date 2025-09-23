#!/usr/bin/env python3
"""
Script principal para o sistema de monitoramento de temperatura via OPC UA.
Permite iniciar servidor, cliente ou visualizador facilmente.
"""

import sys
import os
import subprocess
import time
import argparse
from multiprocessing import Process

def iniciar_servidor():
    """Inicia o servidor OPC UA."""
    print("Iniciando servidor OPC UA...")
    try:
        from servidor_opcua import main as servidor_main
        servidor_main()
    except KeyboardInterrupt:
        print("Servidor parado pelo usuário")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")

def iniciar_cliente():
    """Inicia o cliente OPC UA."""
    print("Iniciando cliente OPC UA...")
    try:
        from cliente_opcua import main as cliente_main
        cliente_main()
    except KeyboardInterrupt:
        print("Cliente parado pelo usuário")
    except Exception as e:
        print(f"Erro ao iniciar cliente: {e}")

def iniciar_visualizador():
    """Inicia o visualizador gráfico."""
    print("Iniciando visualizador gráfico...")
    try:
        from visualizador import main as visualizador_main
        visualizador_main()
    except KeyboardInterrupt:
        print("Visualizador parado pelo usuário")
    except Exception as e:
        print(f"Erro ao iniciar visualizador: {e}")

def iniciar_sistema_completo():
    """Inicia servidor e visualizador simultaneamente."""
    print("Iniciando sistema completo...")
    print("Servidor OPC UA será iniciado em processo separado")
    print("Aguarde alguns segundos e então o visualizador será aberto")
    
    # Iniciar servidor em processo separado
    processo_servidor = Process(target=iniciar_servidor)
    processo_servidor.start()
    
    try:
        # Aguardar servidor inicializar
        print("Aguardando servidor inicializar...")
        time.sleep(5)
        
        # Iniciar visualizador
        iniciar_visualizador()
        
    except KeyboardInterrupt:
        print("Sistema parado pelo usuário")
    
    finally:
        # Parar servidor
        print("Parando servidor...")
        processo_servidor.terminate()
        processo_servidor.join(timeout=5)
        if processo_servidor.is_alive():
            processo_servidor.kill()

def mostrar_status_servidor():
    """Verifica se o servidor está rodando."""
    try:
        from cliente_opcua import ClienteOPCUA
        
        cliente = ClienteOPCUA()
        if cliente.conectar():
            stats = cliente.obter_estatisticas()
            cliente.desconectar()
            
            if stats:
                print("✅ Servidor OPC UA está ONLINE")
                print(f"   Temperatura atual: {stats['atual']:.2f}°C")
                print(f"   Status: {stats['status']}")
                print(f"   Total de leituras: {stats['total_leituras']}")
            else:
                print("⚠️  Servidor conectado mas sem dados")
        else:
            print("❌ Servidor OPC UA está OFFLINE")
            print("   Execute: python main.py servidor")
            
    except Exception as e:
        print(f"❌ Erro ao verificar servidor: {e}")

def mostrar_ajuda():
    """Mostra informações de ajuda."""
    print("""
=== Sistema de Monitoramento de Temperatura via OPC UA ===

Este sistema simula um sensor de temperatura ambiente e disponibiliza
os dados através do protocolo OPC UA com visualização gráfica em tempo real.

COMPONENTES:
• Servidor OPC UA: Simula sensor de temperatura com variações realísticas
• Cliente OPC UA: Conecta ao servidor e coleta dados
• Visualizador: Mostra gráficos em tempo real da temperatura

COMANDOS DISPONÍVEIS:

python main.py servidor
    Inicia apenas o servidor OPC UA
    O servidor ficará disponível em: opc.tcp://localhost:4840/sensor/temperatura

python main.py cliente  
    Inicia apenas o cliente OPC UA (requer servidor rodando)
    Mostra dados no terminal com estatísticas

python main.py visualizador
    Inicia apenas o visualizador gráfico (requer servidor rodando)
    Abre janela com 4 gráficos em tempo real

python main.py completo
    Inicia servidor + visualizador automaticamente
    Modo recomendado para demonstração

python main.py status
    Verifica se o servidor está rodando e mostra informações

python main.py --help
    Mostra esta ajuda

REQUISITOS:
• Python 3.6+
• Bibliotecas: opcua, matplotlib, numpy
• Instale com: pip install -r requirements.txt

ARQUITETURA:
┌─────────────────┐    OPC UA     ┌──────────────────┐
│ Servidor OPC UA │◄──────────────┤ Cliente/Monitor  │
│ (Sensor Virtual)│    TCP/IP     │  (Visualizador)  │
└─────────────────┘               └──────────────────┘

VARIÁVEIS OPC UA DISPONÍVEIS:
• SensorTemperatura/Temperatura (Float) - Valor atual em °C
• SensorTemperatura/Timestamp (String) - Hora da leitura
• SensorTemperatura/Status (String) - Status do sensor
• SensorTemperatura/Unidade (String) - Unidade de medida
• SensorTemperatura/Configuracao/* - Parâmetros do sensor

CARACTERÍSTICAS DO SENSOR SIMULADO:
• Temperatura base: 22°C ± 8°C (variação diária)
• Ruído: ±0.5°C (flutuações naturais)
• Tendências: Pequenas mudanças ao longo do tempo
• Faixa: 10°C a 40°C (limitado para realismo)
• Frequência: Leitura a cada 1 segundo

DICAS:
• Para parar qualquer componente: Ctrl+C
• O visualizador mostra zona de conforto térmico (20-26°C)
• Dados são mantidos em memória (últimas 300 leituras)
• Sistema funciona apenas localmente (localhost)
""")

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Sistema de Monitoramento de Temperatura via OPC UA',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'comando',
        nargs='?',
        choices=['servidor', 'cliente', 'visualizador', 'completo', 'status'],
        default='completo',
        help='Comando a executar (padrão: completo)'
    )
    
    args = parser.parse_args()
    
    # Mostrar cabeçalho
    print("=" * 60)
    print("    SISTEMA DE MONITORAMENTO DE TEMPERATURA OPC UA")
    print("=" * 60)
    print()
    
    # Executar comando
    if args.comando == 'servidor':
        iniciar_servidor()
    elif args.comando == 'cliente':
        iniciar_cliente()
    elif args.comando == 'visualizador':
        iniciar_visualizador()
    elif args.comando == 'completo':
        iniciar_sistema_completo()
    elif args.comando == 'status':
        mostrar_status_servidor()
    else:
        mostrar_ajuda()

if __name__ == "__main__":
    main()