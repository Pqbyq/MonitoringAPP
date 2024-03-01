from influxdb import InfluxDBClient
from datetime import datetime
from kubernetes.client.rest import ApiException
from KubernetesMetrics.kubernetes_metrics import get_cluster_metrics
import time

influxdb_client = InfluxDBClient('localhost', 8086, 'root', 'root', 'mydb')

def create_database():
    databases = influxdb_client.get_list_database()
    if {'name': 'mydb'} not in databases:
        influxdb_client.create_database('mydb')

def write_metrics_to_influxdb(metrics):
    json_body = [
        {
            "measurement": "pod_metrics",
            "tags": {
                "namespace": metric['namespace'],
                "name": metric['name'],
                "status": metric['status']
            },
            "time": datetime.utcnow(),
            "fields": {
                "cpu_usage": metric['cpu_usage'],
                "memory_usage": metric['memory_usage']
            }
        } for metric in metrics
    ]

    influxdb_client.write_points(json_body)

if __name__ == '__main__':
    create_database()

    while True:
        try:
            metrics = get_cluster_metrics(namespace="default")
            write_metrics_to_influxdb(metrics)
            time.sleep(10)  # Poczekaj 10 sekund przed pobraniem kolejnych metryk
        except ApiException as e:
            print("Error:", e)
