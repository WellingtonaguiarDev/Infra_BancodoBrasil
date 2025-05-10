import pandas as pd
import time
import os
from prometheus_client import Gauge, start_http_server

# Configurações
CSV_PATH = os.getenv("CSV_PATH", "metrics.csv")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 5))  # Intervalo em segundos
GPUS = ["GPU_0", "GPU_1", "GPU_2", "GPU_3"]

# Limites máximos por métrica
MAX_METRICS = {
    'gpu_utilization': 55,
    'memory_utilization': 60,
    'gpu_temperature': 60,
    'gpu_power_draw': 130,
    'gpu_fan_speed': 75
}

# Pesos de prioridade para cálculo de score
PRIORITY_WEIGHTS = {
    'gpu_temperature': 0.4,
    'gpu_utilization': 0.3,
    'memory_utilization': 0.2,
    'gpu_power_draw': 0.1
}

# Carrega o CSV
df = pd.read_csv(CSV_PATH)
df['timestamp'] = pd.to_datetime(df['timestamp'])
timestamps = df['timestamp'].unique()

# Inicializa o Prometheus
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
print("Monitoramento otimizado iniciado em http://localhost:8000")

# --- FUNÇÕES ---

def calculate_gpu_score(row):
    score = 0
    for metric, weight in PRIORITY_WEIGHTS.items():
        normalized = row[metric] / MAX_METRICS[metric]
        score += normalized * weight
    return score

def balance_current_load(current_data):
    current_data['score'] = current_data.apply(calculate_gpu_score, axis=1)

    overloaded = current_data[current_data['score'] > 1]
    underloaded = current_data[current_data['score'] <= 1]

    if not overloaded.empty:
        reclaimed = {metric: 0 for metric in PRIORITY_WEIGHTS}

        for idx, row in overloaded.iterrows():
            for metric in PRIORITY_WEIGHTS:
                diff = row[metric] - MAX_METRICS[metric]
                if diff > 0:
                    reclaimed[metric] += diff
                    current_data.at[idx, metric] = MAX_METRICS[metric]

        if not underloaded.empty:
            for metric, reclaim in reclaimed.items():
                if reclaim > 0:
                    per_gpu = reclaim / len(underloaded)
                    for idx in underloaded.index:
                        atual = current_data.at[idx, metric]
                        current_data.at[idx, metric] = min(atual + per_gpu, MAX_METRICS[metric])

    current_data.drop(columns=["score"], inplace=True)
    return current_data

# --- LOOP PRINCIPAL ---

i = 0
while True:
    current_time = timestamps[i]
    current_data = df[df['timestamp'] == current_time].copy()

    balanced_data = balance_current_load(current_data)

    for gpu in GPUS:
        gpu_row = balanced_data[balanced_data['gpu_id'] == gpu]
        if not gpu_row.empty:
            gpu_data = gpu_row.iloc[0]
            metrics['gpu']['utilization'][gpu].set(gpu_data['gpu_utilization'])
            metrics['gpu']['memory_utilization'][gpu].set(gpu_data['memory_utilization'])
            metrics['gpu']['power_draw'][gpu].set(gpu_data['gpu_power_draw'])
            metrics['gpu']['temperature'][gpu].set(gpu_data['gpu_temperature'])
            metrics['gpu']['fan_speed'][gpu].set(gpu_data['gpu_fan_speed'])
            metrics['gpu']['clock_speed'][gpu].set(gpu_data['gpu_clock_speed'])

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
