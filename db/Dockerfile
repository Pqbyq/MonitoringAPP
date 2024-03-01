FROM influxdb:latest

# Instalacja narzędzia influx
RUN apt-get update && \
    apt-get install -y influxdb-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
