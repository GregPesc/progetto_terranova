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

```
git clone https://github.com/GregPesc/progetto_terranova.git
cd progetto_terranova
docker pull ghcr.io/gregpesc/progetto_terranova-app:latest
docker pull ghcr.io/gregpesc/progetto_terranova-caddy:latest
docker compose up -d
```
