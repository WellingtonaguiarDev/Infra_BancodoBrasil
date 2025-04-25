import pandas as pd
import time
import os
from prometheus_client import Gauge, start_http_server

# Configurações
GPU_ID = os.getenv("GPU_ID", "GPU_0")
CSV_PATH = os.getenv("CSV_PATH", "metrics.csv")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 5))

# Carrega os dados
df = pd.read_csv(CSV_PATH)
df = df[df["gpu_id"] == GPU_ID].reset_index(drop=True)

# Define as métricas que vamos expor
gpu_utilization = Gauge('gpu_utilization', 'Utilização da GPU (%)')
gpu_memory_utilization = Gauge('gpu_memory_utilization', 'Utilização da memória da GPU (%)')
gpu_power_draw = Gauge('gpu_power_draw', 'Consumo de energia da GPU (W)')
gpu_temperature = Gauge('gpu_temperature', 'Temperatura da GPU (°C)')
gpu_fan_speed = Gauge('gpu_fan_speed', 'Velocidade do ventilador da GPU (RPM)')
gpu_clock_speed = Gauge('gpu_clock_speed', 'Velocidade do clock da GPU (MHz)')

cpu_utilization = Gauge('cpu_utilization', 'Utilização da CPU (%)')
server_memory_usage = Gauge('server_memory_usage', 'Uso de memória do servidor (%)')
server_power_draw = Gauge('server_power_draw', 'Consumo de energia do servidor (W)')
server_temperature = Gauge('server_temperature', 'Temperatura do servidor (°C)')
server_disk_usage = Gauge('server_disk_usage', 'Uso de disco do servidor (%)')
network_bandwidth = Gauge('network_bandwidth', 'Largura de banda de rede (Mbps)')

# Inicia o servidor Prometheus na porta 8000
start_http_server(8000)

print(f"Simulando métricas para {GPU_ID}...")

# Loop da simulação
i = 0
while True:
    row = df.iloc[i]

    # Atualiza as métricas
    gpu_utilization.set(row['gpu_utilization'])
    gpu_memory_utilization.set(row['memory_utilization'])
    gpu_power_draw.set(row['gpu_power_draw'])
    gpu_temperature.set(row['gpu_temperature'])
    gpu_fan_speed.set(row['gpu_fan_speed'])
    gpu_clock_speed.set(row['gpu_clock_speed'])
    
    cpu_utilization.set(row['cpu_utilization'])
    server_memory_usage.set(row['memory_usage'])
    server_power_draw.set(row['server_power_draw'])
    server_temperature.set(row['server_temperature'])
    server_disk_usage.set(row['disk_usage'])
    network_bandwidth.set(row['network_bandwidth'])

    print(f"[{i}] Atualizado com dados de {row['timestamp']}")
    
    i = (i + 1) % len(df)  # Loop infinito
    time.sleep(UPDATE_INTERVAL)
