# MemoryMaster-Backend Anleitung
## Installation
- Python Version 3.9.6
- Alle Dependencies installieren: `pip install -r requirements.txt` (keine Ahnung ob der Befehl stimmt, Copilot hat ihn vorgeschlagen)
- Docker installieren (Ist auf Windows anders als auf Mac)
- Datenbank-Zeugs konfigurieren: 
  - TablePlus installieren
  - Dort eine neue Datenbank erstellen
  - Daten aus der `database_connection.py` auslesen für Passwort und so
- Docker Container starten: `docker-compose up` ins Terminal eingeben
- Datenbank-Connection abchecken (kann manchmal dauern)
- Service starten: `uvicorn app.main:app --reload` ins Terminal eingeben
- Wenn kein Fehler kommt sollte alles passen
## API-Docs
- API-Docs sind unter `http://localhost:8000/docs` zu finden
## Fragen? -> Nö