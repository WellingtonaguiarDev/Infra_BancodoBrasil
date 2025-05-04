import pandas as pd
import time
import os
from prometheus_client import Gauge, start_http_server

# Configurações
CSV_PATH = os.getenv("CSV_PATH", "metrics.csv")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 5))  # Intervalo padrão de 5 segundos
GPUS = ["GPU_0", "GPU_1", "GPU_2", "GPU_3"]

# Parâmetros de Balanceamento
MAX_METRICS = {
    'gpu_utilization': 65,
    'memory_utilization': 70,
    'gpu_temperature': 70,
    'gpu_power_draw': 150,
    'gpu_fan_speed': 90
}

PRIORITY_WEIGHTS = {
    'gpu_temperature': 0.4,
    'gpu_utilization': 0.3,
    'memory_utilization': 0.2,
    'gpu_power_draw': 0.1
}

# Carrega os dados
df = pd.read_csv(CSV_PATH)
df['timestamp'] = pd.to_datetime(df['timestamp'])
timestamps = df['timestamp'].unique()

# Cria as métricas com sufixo _optimized
metrics = {
    'gpu': {
        'utilization': {gpu: Gauge(f'{gpu.lower()}_utilization_optimized', f'Utilização otimizada da {gpu} (%)') for gpu in GPUS},
        'memory_utilization': {gpu: Gauge(f'{gpu.lower()}_memory_util_optimized', f'Memória otimizada da {gpu} (%)') for gpu in GPUS},
        'power_draw': {gpu: Gauge(f'{gpu.lower()}_power_optimized', f'Energia otimizada da {gpu} (W)') for gpu in GPUS},
        'temperature': {gpu: Gauge(f'{gpu.lower()}_temp_optimized', f'Temperatura otimizada da {gpu} (°C)') for gpu in GPUS},
        'fan_speed': {gpu: Gauge(f'{gpu.lower()}_fan_optimized', f'Fan otimizado da {gpu} (%)') for gpu in GPUS},
        'clock_speed': {gpu: Gauge(f'{gpu.lower()}_clock_optimized', f'Clock otimizado da {gpu} (MHz)') for gpu in GPUS},
    },
    'server': {
        'cpu_utilization': Gauge('server_cpu_optimized', 'CPU otimizada do Servidor (%)'),
        'memory_usage': Gauge('server_mem_optimized', 'Memória otimizada do Servidor (%)'),
        'power_draw': Gauge('server_power_optimized', 'Energia otimizada do Servidor (W)'),
        'temperature': Gauge('server_temp_optimized', 'Temperatura otimizada do Servidor (°C)'),
        'disk_usage': Gauge('server_disk_optimized', 'Disco otimizado do Servidor (%)'),
        'network_bandwidth': Gauge('server_net_optimized', 'Rede otimizada do Servidor (Mbps)'),
    }
}

start_http_server(8000)
print("Monitoramento otimizado iniciado...")

def calculate_gpu_score(row):
    score = 0
    for metric, weight in PRIORITY_WEIGHTS.items():
        normalized = row[metric] / MAX_METRICS[metric]
        score += normalized * weight
    return score

def balance_current_load(current_data):
    scores = current_data.apply(calculate_gpu_score, axis=1)
    overloaded = current_data[scores > 1]

    if not overloaded.empty:
        excess = {}
        for metric in PRIORITY_WEIGHTS:
            total = current_data[metric].sum()
            excess[metric] = total - (MAX_METRICS[metric] * len(GPUS))

        for idx, row in current_data.iterrows():
            if row['gpu_id'] in overloaded['gpu_id'].values:
                for metric in PRIORITY_WEIGHTS:
                    current_data.at[idx, metric] = min(row[metric], MAX_METRICS[metric])

        underloaded = current_data[~current_data['gpu_id'].isin(overloaded['gpu_id'])]
        for metric, excess_value in excess.items():
            if excess_value > 0 and not underloaded.empty:
                per_gpu = excess_value / len(underloaded)
                for idx in underloaded.index:
                    current_data.at[idx, metric] = min(
                        current_data.at[idx, metric] + per_gpu,
                        MAX_METRICS[metric]
                    )

    return current_data

i = 0
while True:
    current_time = timestamps[i]
    current_data = df[df['timestamp'] == current_time].copy()

    # Aplica balanceamento
    balanced_data = balance_current_load(current_data)

    # Atualiza métricas das GPUs
    for gpu in GPUS:
        gpu_data = balanced_data[balanced_data['gpu_id'] == gpu].iloc[0]

        metrics['gpu']['utilization'][gpu].set(gpu_data['gpu_utilization'])
        metrics['gpu']['memory_utilization'][gpu].set(gpu_data['memory_utilization'])
        metrics['gpu']['power_draw'][gpu].set(gpu_data['gpu_power_draw'])
        metrics['gpu']['temperature'][gpu].set(gpu_data['gpu_temperature'])
        metrics['gpu']['fan_speed'][gpu].set(gpu_data['gpu_fan_speed'])
        metrics['gpu']['clock_speed'][gpu].set(gpu_data['gpu_clock_speed'])

    # Atualiza métricas do servidor
    server_data = balanced_data.iloc[0]
    metrics['server']['cpu_utilization'].set(server_data['cpu_utilization'])
    metrics['server']['memory_usage'].set(server_data['memory_usage'])
    metrics['server']['power_draw'].set(server_data['server_power_draw'])
    metrics['server']['temperature'].set(server_data['server_temperature'])
    metrics['server']['disk_usage'].set(server_data['disk_usage'])
    metrics['server']['network_bandwidth'].set(server_data['network_bandwidth'])

    print(f"Timestamp {current_time} processado | GPUs balanceadas: {list(balanced_data['gpu_id'])}")
    i = (i + 1) % len(timestamps)
    time.sleep(UPDATE_INTERVAL)
