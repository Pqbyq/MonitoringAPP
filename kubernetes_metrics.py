# utils.py
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import time
from datetime import datetime 

def convert_to_readable(value):
    units = {'K': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12, 'P': 1e15, 'E': 1e18, 'Z': 1e21, 'Y': 1e24, 'n': 1e-9,
             'Ki': 1024, 'Mi': 1024 ** 2, 'Gi': 1024 ** 3, 'Ti': 1024 ** 4, 'Pi': 1024 ** 5, 'Ei': 1024 ** 6}

    for unit in units:
        if value.endswith(unit):
            numeric_value = float(value[:-len(unit)])
            converted_value = numeric_value * units[unit]
            return round(converted_value, 2)

    return round(float(value), 2)





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
                'memory_usage': memory_usage
            })

    return cluster_metrics

if __name__ == '__main__':
    while True:
        try:
            metrics = get_cluster_metrics(namespace="default")
            print(metrics)
            time.sleep(10)  # Poczekaj 10 sekund przed pobraniem kolejnych metryk
        except ApiException as e:
            print("Error:", e)
