# Drink a Drink

Applicazione web per i cocktail.

# Come eseguire l'applicazione

Testato con python 3.13.1 su Windows.

```
python --version
```

## Setup

Apri un terminale nella directory che preferisci ed esegui i seguenti comandi:

```
git clone https://github.com/GregPesc/progetto_terranova.git
cd progetto_terranova
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Avviare l'applicazione

Attiva il virtual environment ed esegui l'applicazione:

```
.\venv\Scripts\activate
python app\run.py
```

**NOTA**: se vengono fatti cambiamenti alla struttura del database (`models.py`) elimina la directory `instance` (che contiene il file db) prima di eseguire l'applicazione.
