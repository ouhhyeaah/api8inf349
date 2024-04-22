### COMMANDES

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
docker run --network local_api8inf349 -e REDIS_URL=redis://redis -e DB_HOST=postgres -e DB_USER=admin -e DB_PASSWORD=pass -e DB_PORT=5432 -e DB_NAME=api8inf349 --rm -p 5000:5000 <image_tag>
<image_tag> => api8inf349
```
