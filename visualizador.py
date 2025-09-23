#!/usr/bin/env python3
"""
Visualizador gráfico em tempo real para dados do sensor de temperatura via OPC UA.
Mostra gráficos animados da temperatura coletada do servidor OPC UA.
"""

import time
import threading
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime, timedelta
from cliente_opcua import ClienteOPCUA

class VisualizadorTemperatura:
    """Classe para visualização gráfica dos dados de temperatura."""
    
    def __init__(self, endpoint="opc.tcp://localhost:4840/sensor/temperatura"):
        self.cliente = ClienteOPCUA(endpoint)
        self.fig, self.axes = plt.subplots(2, 2, figsize=(15, 10))
        self.fig.suptitle('Monitor de Temperatura - Sensor OPC UA', fontsize=16, fontweight='bold')
        
        # Configurar subplots
        self.ax_tempo_real = self.axes[0, 0]
        self.ax_historico = self.axes[0, 1]
        self.ax_distribuicao = self.axes[1, 0]
        self.ax_estatisticas = self.axes[1, 1]
        
        # Dados para os gráficos
        self.max_pontos = 300  # 5 minutos de dados
        self.x_data = []
        self.y_data = []
        
        # Configurações de animação
        self.animation = None
        self.executando = False
        
        # Configurar estilo
        plt.style.use('seaborn-v0_8')
        
    def configurar_graficos(self):
        """Configura a aparência dos gráficos."""
        
        # Gráfico 1: Temperatura em tempo real
        self.ax_tempo_real.set_title('Temperatura em Tempo Real', fontweight='bold')
        self.ax_tempo_real.set_xlabel('Tempo')
        self.ax_tempo_real.set_ylabel('Temperatura (°C)')
        self.ax_tempo_real.grid(True, alpha=0.3)
        self.ax_tempo_real.set_ylim(15, 35)
        
        # Gráfico 2: Histórico das últimas horas
        self.ax_historico.set_title('Histórico - Últimas 5 Minutos', fontweight='bold')
        self.ax_historico.set_xlabel('Tempo')
        self.ax_historico.set_ylabel('Temperatura (°C)')
        self.ax_historico.grid(True, alpha=0.3)
        
        # Gráfico 3: Distribuição de temperatura
        self.ax_distribuicao.set_title('Distribuição de Temperatura', fontweight='bold')
        self.ax_distribuicao.set_xlabel('Temperatura (°C)')
        self.ax_distribuicao.set_ylabel('Frequência')
        self.ax_distribuicao.grid(True, alpha=0.3)
        
        # Gráfico 4: Estatísticas em texto
        self.ax_estatisticas.set_title('Estatísticas', fontweight='bold')
        self.ax_estatisticas.axis('off')
        
        # Ajustar layout
        plt.tight_layout()
    
    def atualizar_grafico(self, frame):
        """Função chamada pela animação para atualizar os gráficos."""
        try:
            if not self.cliente.conectado:
                return
            
            # Obter dados do cliente
            temps, times = self.cliente.obter_historico(self.max_pontos)
            stats = self.cliente.obter_estatisticas()
            
            if not temps or not times:
                return
            
            # Limpar gráficos
            self.ax_tempo_real.clear()
            self.ax_historico.clear()
            self.ax_distribuicao.clear()
            self.ax_estatisticas.clear()
            
            # Reconfigurar após clear
            self.ax_tempo_real.set_title('Temperatura em Tempo Real', fontweight='bold')
            self.ax_tempo_real.set_ylabel('Temperatura (°C)')
            self.ax_tempo_real.grid(True, alpha=0.3)
            
            self.ax_historico.set_title('Histórico - Últimas 5 Minutos', fontweight='bold')
            self.ax_historico.set_ylabel('Temperatura (°C)')
            self.ax_historico.grid(True, alpha=0.3)
            
            self.ax_distribuicao.set_title('Distribuição de Temperatura', fontweight='bold')
            self.ax_distribuicao.set_xlabel('Temperatura (°C)')
            self.ax_distribuicao.set_ylabel('Frequência')
            self.ax_distribuicao.grid(True, alpha=0.3)
            
            self.ax_estatisticas.set_title('Estatísticas', fontweight='bold')
            self.ax_estatisticas.axis('off')
            
            # Gráfico 1: Últimos 60 pontos para tempo real
            if len(temps) > 60:
                temps_recentes = temps[-60:]
                times_recentes = times[-60:]
            else:
                temps_recentes = temps
                times_recentes = times
            
            if temps_recentes:
                # Converter timestamps para minutos relativos
                tempo_base = times_recentes[0]
                minutos = [(t - tempo_base).total_seconds() / 60 for t in times_recentes]
                
                self.ax_tempo_real.plot(minutos, temps_recentes, 'b-', linewidth=2, alpha=0.8)
                self.ax_tempo_real.scatter(minutos[-1:], temps_recentes[-1:], color='red', s=50, zorder=5)
                
                # Configurar eixo x com rótulos de tempo
                if len(minutos) > 1:
                    self.ax_tempo_real.set_xlim(minutos[0], minutos[-1])
                
                # Zona de conforto térmico
                self.ax_tempo_real.axhspan(20, 26, alpha=0.2, color='green', label='Zona de Conforto')
                self.ax_tempo_real.legend()
            
            # Gráfico 2: Histórico completo
            if len(temps) >= 2:
                tempo_base = times[0]
                minutos_hist = [(t - tempo_base).total_seconds() / 60 for t in times]
                
                self.ax_historico.plot(minutos_hist, temps, 'g-', linewidth=1.5, alpha=0.7)
                
                # Média móvel
                if len(temps) > 10:
                    window = min(10, len(temps))
                    media_movel = np.convolve(temps, np.ones(window)/window, mode='valid')
                    minutos_media = minutos_hist[window-1:]
                    self.ax_historico.plot(minutos_media, media_movel, 'r--', 
                                         linewidth=2, alpha=0.8, label='Média Móvel')
                    self.ax_historico.legend()
            
            # Gráfico 3: Histograma de distribuição
            if len(temps) > 5:
                bins = min(20, len(temps) // 3)
                self.ax_distribuicao.hist(temps, bins=bins, alpha=0.7, color='skyblue', 
                                        edgecolor='black', density=True)
                
                # Linha vertical da média
                if stats:
                    self.ax_distribuicao.axvline(stats['media'], color='red', linestyle='--', 
                                               linewidth=2, alpha=0.8, label=f'Média: {stats["media"]:.1f}°C')
                    self.ax_distribuicao.legend()
            
            # Gráfico 4: Estatísticas em texto
            if stats:
                status_color = 'green' if stats['status'] == 'Online' else 'red'
                
                texto_stats = f"""
STATUS: {stats['status']}

TEMPERATURA ATUAL:
{stats['atual']:.2f}°C

ESTATÍSTICAS:
Média: {stats['media']:.2f}°C
Mínima: {stats['minima']:.2f}°C
Máxima: {stats['maxima']:.2f}°C
Amplitude: {stats['maxima'] - stats['minima']:.2f}°C

DADOS:
Total de leituras: {stats['total_leituras']:,}
Última atualização:
{stats['ultima_atualizacao'].strftime('%H:%M:%S') if stats['ultima_atualizacao'] else 'N/A'}

QUALIDADE DO AR:
{'Muito Frio' if stats['atual'] < 18 else
 'Frio' if stats['atual'] < 20 else
 'Confortável' if stats['atual'] <= 26 else
 'Quente' if stats['atual'] <= 30 else 'Muito Quente'}
                """
                
                self.ax_estatisticas.text(0.05, 0.95, texto_stats, 
                                        transform=self.ax_estatisticas.transAxes,
                                        fontsize=11, verticalalignment='top',
                                        bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
                
                # Indicador de status
                circle = plt.Circle((0.85, 0.9), 0.05, color=status_color, 
                                  transform=self.ax_estatisticas.transAxes)
                self.ax_estatisticas.add_patch(circle)
            
            # Ajustar layout
            plt.tight_layout()
            
        except Exception as e:
            print(f"Erro ao atualizar gráfico: {e}")
    
    def iniciar_visualizacao(self):
        """Inicia a visualização gráfica."""
        try:
            print("Iniciando visualizador de temperatura...")
            
            # Conectar ao servidor OPC UA
            if not self.cliente.conectar():
                print("Erro: Não foi possível conectar ao servidor OPC UA")
                print("Certifique-se de que o servidor está rodando")
                return False
            
            # Iniciar leitura contínua
            self.cliente.iniciar_leitura_continua()
            
            # Aguardar alguns dados iniciais
            print("Aguardando dados iniciais...")
            time.sleep(3)
            
            # Configurar gráficos
            self.configurar_graficos()
            
            # Iniciar animação
            self.executando = True
            self.animation = animation.FuncAnimation(
                self.fig, 
                self.atualizar_grafico,
                interval=1000,  # Atualizar a cada 1 segundo
                blit=False,
                cache_frame_data=False
            )
            
            print("Visualizador iniciado com sucesso!")
            print("Feche a janela do gráfico para parar")
            
            # Mostrar gráfico
            plt.show()
            
            return True
            
        except Exception as e:
            print(f"Erro ao iniciar visualizador: {e}")
            return False
        
        finally:
            self.parar()
    
    def parar(self):
        """Para a visualização."""
        try:
            self.executando = False
            
            if self.animation:
                self.animation.event_source.stop()
            
            self.cliente.desconectar()
            print("Visualizador parado")
            
        except Exception as e:
            print(f"Erro ao parar visualizador: {e}")

def main():
    """Função principal."""
    print("=== Visualizador de Temperatura OPC UA ===")
    print("Este programa conecta ao servidor OPC UA e mostra")
    print("gráficos em tempo real da temperatura do sensor.")
    print()
    
    # Criar e iniciar visualizador
    visualizador = VisualizadorTemperatura()
    visualizador.iniciar_visualizacao()

if __name__ == "__main__":
    main()