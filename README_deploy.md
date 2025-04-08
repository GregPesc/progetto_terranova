# Sviluppo locale con Docker

## Requisiti

- git
- Docker

## Sviluppo in locale

```
git clone https://github.com/GregPesc/progetto_terranova.git
cd progetto_terranova
docker compose -f .\docker-compose-dev.yml up -d --build
```

## Deploy

Vedi [pipeline.yaml](.github/workflows/pipeline.yaml) per deploy tramite Github Actions
