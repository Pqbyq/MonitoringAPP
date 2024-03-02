# Używamy oficjalnego obrazu Python 3.8
FROM python:3.8

# Ustawiamy katalog roboczy wewnątrz kontenera
WORKDIR /app

# Kopiujemy pliki z obecnego katalogu (gdzie znajduje się Dockerfile) do /app w kontenerze
COPY . /app

# Utwórz katalog dla logów
RUN mkdir -p /var/log/metrics-app

# Zmień uprawnienia, aby umożliwić zapis do katalogu logów
RUN chmod -R 777 /var/log/metrics-app

# Dodaj alias do .bashrc
RUN echo "alias app='tail -f /var/log/metrics-app/app.log'" >> ~/.bashrc

# Instalujemy zależności
RUN pip install --no-cache-dir -r requirements.txt

# Wystawiamy port 5000, który nasza aplikacja Flask będzie nasłuchiwać
EXPOSE 5000

# Uruchamiamy aplikację po zbudowaniu obrazu
CMD ["python", "metrics.py"]