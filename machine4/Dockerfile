FROM python:3.9-slim

WORKDIR /app

COPY metrics_exporter.py /app/
COPY metrics.csv /app/

RUN pip install pandas prometheus_client

CMD ["python", "metrics_exporter.py"]
