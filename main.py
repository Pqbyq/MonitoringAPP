from flask import Flask, render_template
from kubernetes_metrics import get_cluster_metrics
from kubernetes.client.rest import ApiException

app = Flask(__name__)

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
