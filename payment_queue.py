## RQ Worker pour traiter les paiements
from rq import Queue, Connection
import redis

# Importez la connexion Redis et la base de données Redis de worker.py
from worker import conn, redis_db

# Import Orders pour le type d'argument
from Models import Orders

import helpers, db  # Importez les fonctions d'aides
import time, json

# Créez une file d'attente RQ avec la connexion Redis
payment_queue = Queue("payment", connection=conn)


# Fonction pour effectuer le paiement
def process_payment(
    state: bool, order_id: int, credit_card: dict, transaction: dict
) -> bool:
    if state:
        payment_queue.enqueue(
            process_successfull_payment_task,
            order_id,
            credit_card,
            transaction,
            state,
        )
        time.sleep(2)  # Simuler un traitement de paiement de 2 secondes
        return True  # Retournez True si le paiement est réussi
    else:
        payment_queue.enqueue(
            process_failed_payment_task,
            order_id,
            transaction,
            helpers.get_amount_charged(order_id),
        )
        time.sleep(2)
        return False  # Retournez False si le paiement a échoué


def process_successfull_payment_task(
    order_id: int, credit_card: dict, transaction: dict, state: bool
) -> None:
    print("Processing payment...")
    transaction["errors"] = {}
    db.put_credit_card_info(order_id, credit_card, transaction, True)
    cache_order(order_id, db.get_order_by_id(order_id))


def process_failed_payment_task(
    order_id: int, _transaction: dict, amount_charged: float
) -> None:
    credit_card = {}
    transaction = {
        "success": False,
        "error": {
            "code": _transaction["errors"]["credit_card"]["code"],
            "name": _transaction["errors"]["credit_card"]["name"],
        },
        "amount_charged": amount_charged,
    }
    db.put_credit_card_info(order_id, credit_card, transaction, False)


# Fonction pour vérifier si une commande est dans la file d'attente
def check_queue(order_id) -> bool:
    # Établir une connexion à la file d'attente Redis
    with Connection(conn):
        # Accédez à la file d'attente nommée 'default'
        queue = Queue("payment")
        # Parcourez les tâches dans la file d'attente pour voir si l'une d'elles correspond à l'ID de commande donné
        for job in queue.jobs:
            # Vérifiez si l'ID de la commande correspond à l'ID de la commande donné
            if "order_id" in job.meta and job.meta["order_id"] == order_id:
                return True
    return False


def print_queue():
    with Connection(conn):
        queue = Queue("payment")
        jobs = []


def cache_order(order_id: int, order_data: Orders) -> None:
    """Met une commande en cache pour 60 secondes. Utilisation de Redis"""
    db = redis_db()
    # Met la commande en cache pour 60 secondes
    db.set(f"order:{order_id}", json.dumps(helpers.format_order(order_data)), ex=60)
