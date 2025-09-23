# Sistema de Monitoramento de Temperatura via OPC UA

Este projeto implementa um sistema completo de simulação e monitoramento de sensor de temperatura ambiente usando o protocolo OPC UA (Open Platform Communications Unified Architecture).

## 🎯 Características

- **Servidor OPC UA**: Simula um sensor de temperatura com variações realísticas
- **Cliente OPC UA**: Conecta ao servidor e coleta dados em tempo real
- **Visualizador Gráfico**: Interface gráfica com múltiplos gráficos em tempo real
- **Dados Realísticos**: Simula variações diárias, ruído e tendências de temperatura
- **Protocolo Padrão**: Usa OPC UA para comunicação industrial padrão

## 📁 Estrutura do Projeto

```
sensor_temperatura_opcua/
├── main.py              # Script principal para executar o sistema
├── servidor_opcua.py    # Servidor OPC UA que simula o sensor
├── cliente_opcua.py     # Cliente OPC UA para coleta de dados
├── visualizador.py      # Interface gráfica em tempo real
├── requirements.txt     # Dependências Python
└── README.md           # Esta documentação
```

## 🚀 Instalação

### 1. Clonar/Baixar o Projeto
```bash
# Se usando git
git clone <url-do-repositorio>
cd sensor_temperatura_opcua

# Ou baixar e extrair os arquivos em uma pasta
```

### 2. Instalar Dependências Python
```bash
pip install -r requirements.txt
```

### 3. Verificar Instalação
```bash
python main.py status
```

## 🎮 Como Usar

### Opção 1: Sistema Completo (Recomendado)
```bash
python main.py completo
```
- Inicia servidor OPC UA automaticamente
- Abre visualizador gráfico após alguns segundos
- Ideal para demonstrações

### Opção 2: Componentes Separados

**Iniciar apenas o servidor:**
```bash
python main.py servidor
```

**Iniciar apenas o cliente (em outro terminal):**
```bash
python main.py cliente
```

**Iniciar apenas o visualizador (em outro terminal):**
```bash
python main.py visualizador
```

### Verificar Status
```bash
python main.py status
```

### Ajuda
```bash
python main.py --help
```

## 📊 Interface Gráfica

O visualizador mostra 4 gráficos simultâneos:

1. **Temperatura em Tempo Real**: Últimos 60 pontos com destaque da leitura atual
2. **Histórico**: Todas as leituras dos últimos 5 minutos com média móvel
3. **Distribuição**: Histograma das temperaturas coletadas
4. **Estatísticas**: Informações textuais (média, min, max, status, etc.)

### Recursos Visuais:
- Zona de conforto térmico destacada (20-26°C)
- Indicador de status (verde=online, vermelho=erro)
- Classificação qualitativa da temperatura
- Atualização em tempo real (1 segundo)

## 🌡️ Características do Sensor Simulado

### Modelo de Temperatura
- **Temperatura Base**: 22°C
- **Variação Diária**: ±8°C (simulando ciclo dia/noite)
- **Ruído Natural**: ±0.5°C (flutuações naturais)
- **Tendências**: Pequenas mudanças graduais
- **Faixa**: 10°C a 40°C (limitado para realismo)

### Padrão de Variação
```
Temperatura = Base + CicloDiário + Ruído + Tendência

Onde:
- CicloDiário = sin(tempo) * 8°C
- Ruído = random(-0.5, +0.5)°C
- Tendência = deriva gradual ±0.5°C
```

### Frequência
- **Leitura**: A cada 1 segundo
- **Histórico**: Últimas 300 leituras (5 minutos)
- **Persistência**: Apenas em memória

## 🔧 Configuração OPC UA

### Servidor
- **Endpoint**: `opc.tcp://localhost:4840/sensor/temperatura`
- **Namespace**: `http://sensor.temperatura.opcua`
- **Segurança**: None (desenvolvimento)

### Variáveis Disponíveis
```
Objects/
└── SensorTemperatura/
    ├── Temperatura (Float)      # Valor atual em °C
    ├── Timestamp (String)       # ISO timestamp da leitura
    ├── Status (String)          # "Online", "Erro", etc.
    ├── Unidade (String)         # "°C"
    └── Configuracao/
        ├── TempMinima (Float)   # 10.0°C
        ├── TempMaxima (Float)   # 40.0°C
        └── Precisao (Float)     # 0.1°C
```

## 🛠️ Desenvolvimento

### Requisitos
- Python 3.6+
- opcua >= 0.98.13
- matplotlib >= 3.7.2
- numpy >= 1.24.3

### Executar Componentes Individualmente

**Servidor:**
```python
from servidor_opcua import ServidorOPCUA
servidor = ServidorOPCUA()
servidor.iniciar()
```

**Cliente:**
```python
from cliente_opcua import ClienteOPCUA
cliente = ClienteOPCUA()
cliente.conectar()
cliente.iniciar_leitura_continua()
```

**Visualizador:**
```python
from visualizador import VisualizadorTemperatura
viz = VisualizadorTemperatura()
viz.iniciar_visualizacao()
```

### Personalização

**Mudar endpoint:**
```python
servidor = ServidorOPCUA("opc.tcp://192.168.1.100:4840/sensor")
```

**Ajustar parâmetros do sensor:**
```python
sensor = SensorTemperatura()
sensor.temperatura_base = 25.0  # Nova temperatura base
sensor.amplitude_diaria = 5.0   # Menor variação
```

## 🔍 Solução de Problemas

### Erro: "Não foi possível conectar ao servidor"
- Verifique se o servidor está rodando: `python main.py status`
- Inicie o servidor: `python main.py servidor`
- Verifique firewall/antivírus

### Erro: "Módulo opcua não encontrado"
```bash
pip install opcua==0.98.13
```

### Erro: "Não foi possível resolver importação matplotlib"
```bash
pip install matplotlib==3.7.2
```

### Gráficos não aparecem (Linux)
```bash
# Instalar backend gráfico
sudo apt-get install python3-tk
# ou
pip install tkinter
```

### Performance lenta
- Reduza frequência de atualização no visualizador
- Diminua número de pontos no histórico
- Feche outros programas que usam muita CPU

## 📈 Casos de Uso

### Educacional
- Aprender protocolo OPC UA
- Demonstrar comunicação industrial
- Simular sistemas de monitoramento

### Desenvolvimento
- Testar clientes OPC UA
- Prototipagem de dashboards
- Validar arquiteturas IoT

### Demonstração
- Mostrar capacidades do OPC UA
- Simular ambiente industrial
- Apresentações técnicas

## 🔒 Limitações

### Segurança
- **Desenvolvimento apenas**: Sem autenticação/criptografia
- **Rede local**: Funciona apenas em localhost
- **Produção**: Implementar certificados e usuários

### Performance
- **Memória**: Histórico limitado a 300 pontos
- **CPU**: Atualização gráfica pode ser intensiva
- **Rede**: Sem otimizações para WAN

### Funcionalidades
- **Persistência**: Dados não são salvos em disco
- **Configuração**: Parâmetros fixos no código
- **Múltiplos sensores**: Apenas um sensor simulado

## 🚀 Melhorias Futuras

### Funcionalidades
- [ ] Múltiplos sensores (temperatura, umidade, pressão)
- [ ] Configuração via arquivo JSON/YAML
- [ ] Histórico persistente em banco de dados
- [ ] API REST complementar
- [ ] Alertas configuráveis

### Interface
- [ ] Dashboard web (Flask/Django)
- [ ] Configuração gráfica dos parâmetros
- [ ] Exportação de dados (CSV, Excel)
- [ ] Relatórios automáticos

### Segurança
- [ ] Autenticação de usuários
- [ ] Certificados X.509
- [ ] Criptografia de comunicação
- [ ] Logs de auditoria

### Performance
- [ ] Otimização da renderização gráfica
- [ ] Compressão de dados históricos
- [ ] Cache inteligente
- [ ] Suporte a múltiplos clientes

## 📞 Suporte

### Logs
Os componentes geram logs no terminal. Para debug:
```bash
python main.py servidor 2>&1 | tee servidor.log
```

### Problemas Comuns
1. **Porta ocupada**: Mude a porta no endpoint
2. **Permissões**: Execute como administrador se necessário  
3. **Dependências**: Reinstale requirements.txt

### Contato
- Abra issues no repositório
- Consulte documentação OPC UA
- Verifique versões das dependências

---

**Desenvolvido com Python e OPC UA** 🐍🏭