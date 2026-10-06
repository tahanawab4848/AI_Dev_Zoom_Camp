import os
import json

os.makedirs('grafana/provisioning/datasources', exist_ok=True)
os.makedirs('grafana/provisioning/dashboards', exist_ok=True)
os.makedirs('grafana/dashboards', exist_ok=True)

with open('otel-collector-config.yaml', 'w') as f:
    f.write('''receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

exporters:
  prometheus:
    endpoint: 0.0.0.0:8889
  loki:
    endpoint: http://loki:3100/loki/api/v1/push
  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true
  debug:

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [otlp/tempo, debug]
    metrics:
      receivers: [otlp]
      exporters: [prometheus, debug]
    logs:
      receivers: [otlp]
      exporters: [loki, debug]
''')

with open('prometheus.yml', 'w') as f:
    f.write('''global:
  scrape_interval: 5s

scrape_configs:
  - job_name: 'otel-collector'
    static_configs:
      - targets: ['collector:8889']
''')

with open('grafana/provisioning/datasources/datasources.yaml', 'w') as f:
    f.write('''apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
  - name: Tempo
    type: tempo
    access: proxy
    url: http://tempo:3200
''')

with open('grafana/provisioning/dashboards/dashboards.yaml', 'w') as f:
    f.write('''apiVersion: 1
providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /etc/grafana/dashboards
''')

dashboard = {
  "title": "App Dashboard",
  "panels": [
    {
      "type": "timeseries",
      "title": "Request Counts",
      "targets": [
        {
          "expr": "sum(rate(request_counts_total[1m])) by (http_status_code)"
        }
      ],
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 }
    },
    {
      "type": "timeseries",
      "title": "5xx Errors",
      "targets": [
        {
          "expr": "sum(rate(request_counts_total{http_status_code=~\"5..\"}[1m]))"
        }
      ],
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 }
    }
  ]
}

with open('grafana/dashboards/dashboard.json', 'w') as f:
    json.dump(dashboard, f)
