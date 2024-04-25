https://github.com/ouhhyeaah/api8inf349

## Docker

Utilisation d'un réseau personnalisé pour l'ensemble des services. D'où l'argument `--network <DIRECTORY>_api8inf349` lors du lancement du container.

## COMMANDES

### COMMANDES PYTHON

```bash
flask init-db
## Init db
```

```bash
flask drop-db
## Drop db
```

```bash
flask flush
## Drop and init in the same command
```

```bash
flask worker
## Start a worker to process payment tasks.
##    Default number of workers is 1.
##    Can receive an optional argument to start more workers. --number 2 for example.
```

```bash
flask cache
## Afficher le cache
```

### COMMANDES DOCKER

#### Services PostgreSQL et Redis

Afin de démarer les service de base de données Redis et Postgres :

```bash
docker-compose up
```

#### Application

Afin de build l'application depuis le Dockerfile

```bash
docker build -t <image_tag> .
<image_tag> => api8inf349
```

Run l'image

```bash
docker run --network <DIRECTORY>_api8inf349 -e REDIS_URL=redis://redis -e DB_HOST=postgres -e DB_USER=admin -e DB_PASSWORD=pass -e DB_PORT=5432 -e DB_NAME=api8inf349 --rm -p 5000:5000 <image_tag>
# <image_tag> => api8inf349
# <DIRECTORY> => current directory
```
