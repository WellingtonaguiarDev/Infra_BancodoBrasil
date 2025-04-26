# Simulador de Métricas

[![Docker Hub](https://img.shields.io/badge/DockerHub-aguiarzx%2Fmachine1-blue)](https://hub.docker.com/r/aguiarzx/machine1)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repo-blueviolet)](https://github.com/aguiarzx/simulador-metricas)

Este projeto simula a exportação de métricas de GPU utilizando **containers Docker**.  
As métricas são geradas em arquivos CSV e expostas através de um **endpoint HTTP** no padrão do **Prometheus**.

---

## 📂 Estrutura do Projeto

O projeto é dividido em 4 máquinas simuladas:

- **machine1**
- **machine2**
- **machine3**
- **machine4**

Cada máquina:
- Exporta métricas de um arquivo `metrics.csv`
- Atualiza as métricas a cada intervalo de tempo configurável
- Expõe as métricas na porta `8000` (padrão)

---

## 🚀 Tecnologias Utilizadas

- Python 3.9 (Slim)
- Pandas
- Prometheus Client
- Docker
- Kubernetes (para orquestração)

---

## 🛠️ Como Executar Localmente

### 1. Build da Imagem Docker

Entre na pasta da máquina desejada (exemplo: `machine1`) e execute:

```bash
docker build -t aguiarzx/machine1 .
```

### 2. Rodar o Container

```bash
docker run -p 8000:8000 --env GPU_ID=GPU_0 --env CSV_PATH=/app/metrics.csv --env UPDATE_INTERVAL=5 aguiarzx/machine1
```

### 3. Acessar as Métricas

Abra no navegador ou use `curl`:

```bash
http://localhost:8000/metrics
```

---

## ☸️ Como Fazer o Deploy no Kubernetes

1. Aplique o deployment:

```bash
kubectl apply -f deployments/machine1-deployment.yaml
```

2. Verifique se o pod subiu:

```bash
kubectl get pods
```

3. Veja os logs do container:

```bash
kubectl logs <nome-do-pod>
```

---

## ⚙️ Variáveis de Ambiente

| Variável          | Descrição                              | Valor padrão         |
|-------------------|----------------------------------------|-----------------------|
| `GPU_ID`          | Identificação da GPU simulada          | `GPU_0`               |
| `CSV_PATH`        | Caminho do arquivo CSV de métricas     | `/app/metrics.csv`    |
| `UPDATE_INTERVAL` | Intervalo de atualização (segundos)    | `5`                   |

---

## 👨‍💻 Autor

Feito por **Wellington Aguiar** 🚀  
[LinkedIn](#) | [GitHub](https://github.com/aguiarzx)

---