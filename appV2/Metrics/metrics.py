from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.config import ConfigException
from datetime import datetime
from flask import Flask, render_template
from logging.handlers import RotatingFileHandler
import logging
import os

log_dir = '/var/log/metrics-app/'
log_file = 'app.log'

# Sprawdź, czy katalog logów istnieje
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Konfiguracja logowania
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(os.path.join(log_dir, log_file), maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

def convert_to_readable(value):
    units = {'K': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12, 'P': 1e15, 'E': 1e18, 'Z': 1e21, 'Y': 1e24, 'n': 1e-9,
             'Ki': 1024, 'Mi': 1024 ** 2, 'Gi': 1024 ** 3, 'Ti': 1024 ** 4, 'Pi': 1024 ** 5, 'Ei': 1024 ** 6}

    for unit in units:
        if value.endswith(unit):
            numeric_value = float(value[:-len(unit)])
            converted_value = numeric_value * units[unit]
            return round(converted_value, 4)

    return round(float(value), 2)

def get_cluster_metrics(namespace=None):
    try:
    # Load configuration inside the Pod
        config.load_incluster_config()
    except ConfigException:
    # Load configuration for testing
        config.load_kube_config()
    v1 = client.CoreV1Api()

    try:
        pods = v1.list_pod_for_all_namespaces(watch=False)
        metric_server_api = client.CustomObjectsApi()
        pod_metrics_list = metric_server_api.list_cluster_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            plural="pods"
        )
    except ApiException as e:
        app.logger.error(f"Error while fetching metrics: {e}")
        return []

    cluster_metrics = []

    for pod in pods.items:
        if namespace is None or pod.metadata.namespace == namespace:
            pod_name = pod.metadata.name
            pod_status = pod.status.phase

            # Szukaj metryk dla danego poda
            pod_metrics = next((metrics for metrics in pod_metrics_list['items'] if metrics['metadata']['name'] == pod_name), None)

            if pod_metrics:
                cpu_usage = convert_to_readable(pod_metrics['containers'][0]['usage']['cpu'])
                memory_usage = convert_to_readable(pod_metrics['containers'][0]['usage']['memory'])
            else:
                cpu_usage = 'N/A'
                memory_usage = 'N/A'

            cluster_metrics.append({
                'namespace': pod.metadata.namespace,
                'name': pod_name,
                'status': pod_status,
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            })

    return cluster_metrics

@app.route('/')
def index():
    try:
        metrics = get_cluster_metrics(namespace=None)
        return render_template('index.html', metrics=metrics)
    except ApiException as e:
        app.logger.error("Error:", e)
        raise e

if __name__ == '__main__':
    app.run(debug=True)
