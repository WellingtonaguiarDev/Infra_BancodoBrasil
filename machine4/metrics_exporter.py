import pandas as pd
import time
import os
from prometheus_client import Gauge, start_http_server

# Configurações
CSV_PATH = os.getenv("CSV_PATH", "metrics.csv")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 5))

# Carrega todos os dados
df = pd.read_csv(CSV_PATH)

# Separa os dados por GPU
gpus = ["GPU_0", "GPU_1", "GPU_2", "GPU_3"]

# Cria as métricas para cada GPU
metrics = {
    'gpu': {
        'utilization': {gpu: Gauge(f'{gpu.lower()}_utilization', f'Utilização da {gpu} (%)') for gpu in gpus},
        'memory_utilization': {gpu: Gauge(f'{gpu.lower()}_memory_utilization', f'Utilização de memória da {gpu} (%)') for gpu in gpus},
        'power_draw': {gpu: Gauge(f'{gpu.lower()}_power_draw', f'Consumo de energia da {gpu} (W)') for gpu in gpus},
        'temperature': {gpu: Gauge(f'{gpu.lower()}_temperature', f'Temperatura da {gpu} (°C)') for gpu in gpus},
        'fan_speed': {gpu: Gauge(f'{gpu.lower()}_fan_speed', f'Velocidade do fan da {gpu} (%)') for gpu in gpus},
        'clock_speed': {gpu: Gauge(f'{gpu.lower()}_clock_speed', f'Clock speed da {gpu} (MHz)') for gpu in gpus},
    },
    'server': {
        'cpu_utilization': Gauge('cpu_utilization', 'Utilização da CPU (%)'),
        'memory_usage': Gauge('server_memory_usage', 'Uso de memória do servidor (%)'),
        'power_draw': Gauge('server_power_draw', 'Consumo de energia do servidor (W)'),
        'temperature': Gauge('server_temperature', 'Temperatura do servidor (°C)'),
        'disk_usage': Gauge('server_disk_usage', 'Uso de disco do servidor (%)'),
        'network_bandwidth': Gauge('server_network_bandwidth', 'Largura de banda de rede (Mbps)'),
    }
}

# Inicia o servidor Prometheus
start_http_server(8000)

print(f"Simulando métricas para todas GPUs e servidor...")

# Loop principal
timestamps = df['timestamp'].unique()
i = 0

while True:
    timestamp = timestamps[i]
    rows = df[df['timestamp'] == timestamp]

    for gpu in gpus:
        row = rows[rows['gpu_id'] == gpu].iloc[0]
        
        # Atualiza métricas das GPUs
        metrics['gpu']['utilization'][gpu].set(row['gpu_utilization'])
        metrics['gpu']['memory_utilization'][gpu].set(row['memory_utilization'])
        metrics['gpu']['power_draw'][gpu].set(row['gpu_power_draw'])
        metrics['gpu']['temperature'][gpu].set(row['gpu_temperature'])
        metrics['gpu']['fan_speed'][gpu].set(row['gpu_fan_speed'])
        metrics['gpu']['clock_speed'][gpu].set(row['gpu_clock_speed'])

    # Atualiza métricas do servidor (pega da primeira linha apenas)
    server_row = rows.iloc[0]
    metrics['server']['cpu_utilization'].set(server_row['cpu_utilization'])
    metrics['server']['memory_usage'].set(server_row['memory_usage'])
    metrics['server']['power_draw'].set(server_row['server_power_draw'])
    metrics['server']['temperature'].set(server_row['server_temperature'])
    metrics['server']['disk_usage'].set(server_row['disk_usage'])
    metrics['server']['network_bandwidth'].set(server_row['network_bandwidth'])

    print(f"[{i}] Atualizado com dados de {timestamp}")
    i = (i + 1) % len(timestamps)

    time.sleep(UPDATE_INTERVAL)