# Description: Ce fichier est utilisé pour démarrer le travailleur RQ.
import redis, json
from rq import Worker, Queue, Connection
import os
from dotenv import load_dotenv

load_dotenv()  # Load the .env file for local testing

# Définir la connexion Redis
# Assurez-vous que les informations de connexion correspondent à votre configuration Redis
REDIS_URL = os.getenv("REDIS_URL")
conn = redis.from_url(REDIS_URL)


def redis_db() -> redis.Redis:
    db = redis.from_url(REDIS_URL)
    # make sure redis is up and running
    db.ping()
    return db


if __name__ == "__main__":
    with Connection(conn):
        worker = Worker(Queue(), connection=conn)
        worker.work()
