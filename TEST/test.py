from kubernetes import client, config
from kubernetes.client.rest import ApiException
from flask import Flask, render_template
import os

app = Flask(__name__)

# Pobierz katalog bieżący (bieżący katalog, w którym znajduje się plik test.py)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Konfiguracja klienta do łączenia się z API Kubernetes
config.load_kube_config()

# Aktualizacja funkcji get_cluster_metrics w pliku test.py
def get_cluster_metrics(namespace=None, kubeconfig_path='~/.kube/config', context=None):
    config.load_kube_config(config_file=kubeconfig_path, context=context)
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
        print(f"Error while fetching metrics: {e}")
        return []

    cluster_metrics = []

    for pod in pods.items:
        if namespace is None or pod.metadata.namespace == namespace:
            pod_name = pod.metadata.name
            pod_status = pod.status.phase

            # Szukaj metryk dla danego poda
            pod_metrics = next((metrics for metrics in pod_metrics_list['items'] if metrics['metadata']['name'] == pod_name), None)

            if pod_metrics:
                cpu_usage = pod_metrics['containers'][0]['usage']['cpu']
                memory_usage = pod_metrics['containers'][0]['usage']['memory']
            else:
                cpu_usage = 'N/A'
                memory_usage = 'N/A'

            cluster_metrics.append({
                'namespace': pod.metadata.namespace,
                'name': pod_name,
                'status': pod_status,
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage
            })

    return cluster_metrics


# Endpoint do wizualizacji metryk
@app.route('/')
def index():
    try:
        metrics = get_cluster_metrics(namespace="default")
        return render_template('index.html', metrics=metrics)
    except ApiException as e:
        print("Error:", e)
        raise e

if __name__ == '__main__':
    app.run(debug=True)
