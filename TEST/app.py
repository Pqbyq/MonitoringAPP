from flask import Flask, render_template
from kubernetes import client, config
import os

app = Flask(__name__)

# Pobierz katalog bieżący (bieżący katalog, w którym znajduje się plik test.py)
current_directory = os.path.dirname(os.path.abspath(__file__))


def get_cluster_metrics(namespace=None, kubeconfig_path='~/.kube/config', context=None):
    config.load_kube_config(config_file=kubeconfig_path, context=context)
    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces(watch=False)
    cluster_metrics = []
    for pod in pods.items:
        if namespace is None or pod.metadata.namespace == namespace:
            pod_metrics = {
                'namespace': pod.metadata.namespace,
                'name': pod.metadata.name,
                'status': pod.status.phase,
                'cpu_usage': 'N/A',  # Domyślnie ustawione na "N/A", dostosuj zgodnie z rzeczywistymi danymi
                'memory_usage': 'N/A'  # Domyślnie ustawione na "N/A", dostosuj zgodnie z rzeczywistymi danymi
            }
            # Dodaj wypisy dla debugowania
            print(f"Pod Name: {pod.metadata.name}")
            print(f"Container Statuses: {pod.status.container_statuses}")
            # Pobierz informacje o zasobach tylko jeśli są dostępne
            if pod.status.container_statuses:
                container_status = pod.status.container_statuses[0]
                if container_status.usage:
                    pod_metrics['cpu_usage'] = container_status.usage['cpu']
                    pod_metrics['memory_usage'] = container_status.usage['memory']

            cluster_metrics.append(pod_metrics)

    return cluster_metrics


# Endpoint do wizualizacji metryk
@app.route('/')
def index():
    try:
        # Użyj funkcji get_cluster_metrics, aby uzyskać dane z klastra
        metrics = get_cluster_metrics(namespace="default")
        return render_template('index.html', metrics=metrics)
    except Exception as e:
        print("Error:", e)  # Wypisz błąd na konsoli Pythona
        raise e  # Przekaż błąd, aby Flask wyświetlił go jako Internal Server Error


if __name__ == '__main__':
    app.run(debug=True)
