# Drink a Drink
Applicazione web per i cocktail.

# Come eseguire il progetto
## Requisiti
Testato con python 3.13+
```
python --version
```

## Prima volta (Setup)
Apri il terminale nella cartella che preferisci ed esegui i seguenti comandi:
```
git clone https://github.com/GregPesc/progetto_terranova.git
cd progetto_terranova
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app\run.py
```

## Volte successive
Per eseguire/lavorare sul progetto le volte successive.

Attiva il virtual environment con:
```
.\venv\Scripts\activate
```
E esegui l'applicazione con:
```
python app\run.py
```

**NOTA**: se vengono fatti cambiamenti alla struttura del database, elimina la cartella `instance` (che contiene il file db) prima di rieseguire l'applicazione.