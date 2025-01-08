# 1. Basis-Image verwenden
FROM python:3.11-slim

# 2. Arbeitsverzeichnis erstellen und setzen
WORKDIR /app

# 3. System-Abhängigkeiten installieren (falls benötigt)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Abhängigkeiten installieren
# Kopiere nur die Requirements-Datei, um Caching zu nutzen
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Quellcode in den Container kopieren
COPY . .

# 6. Port für den Service freigeben
EXPOSE 8000

# 7. Start-Befehl definieren
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
