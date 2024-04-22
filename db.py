# ORM pour la base de données PostgreSQL
from peewee import PostgresqlDatabase

# Importez les modèles Products et Orders
from Models import Products, Orders

# Import module pour les requêtes HTTP, et le module json pour le traitement des données JSON
import json, requests

# Importez les fonctions d'aide
import helpers

# Pour les variables d'environnement
import os
from dotenv import load_dotenv

load_dotenv()
# Configuration de la base de données PostgreSQL avec Peewee
# DATABASE = os.getenv("POSTGRES_DB")
# # USER = os.getenv("POSTGRES_USER")
# PASSWORD = os.getenv("POSTGRES_PASSWORD")
DATABASE = os.getenv("DB_NAME")
HOST = os.getenv("DB_HOST")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
PORT = os.getenv("DB_PORT")
pg_db = PostgresqlDatabase(DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)

# URL de l'API
API_URL = "http://dimprojetu.uqac.ca/~jgnault/shops/products/"


def query_API() -> dict:
    response = requests.get(API_URL)
    if response.status_code == 200:
        json_response = response.json()
        return json_response["products"]
    else:
        return {"errors": response.raise_for_status()}


# Utile car la commande n°45 à un caractère nul à la fin de la chaîne de caractères
def clean_string(s: str):
    return s.replace("\x00", "")


def create_tables():
    pg_db.connect()
    pg_db.create_tables([Products, Orders])
    populate_db()
    pg_db.close()


def drop_tables():
    pg_db.connect()
    pg_db.drop_tables([Products, Orders])
    pg_db.close()


def populate_db():
    products = query_API()
    for product in products:
        Products.create(
            name=clean_string(product["name"]),
            type=clean_string(product["type"]),
            description=clean_string(product["description"]),
            image=clean_string(product["image"]),
            height=product["height"],
            weight=product["weight"],
            price=product["price"],
            in_stock=product["in_stock"],
        )


def flush():
    drop_tables()
    create_tables()


def query_all_products():
    products = []
    for product in Products.select():
        products.append(
            {
                "id": product.id,
                "name": product.name,
                "type": product.type,
                "description": product.description,
                "image": product.image,
                "height": product.height,
                "weight": product.weight,
                "price": product.price,
                "in_stock": product.in_stock,
            }
        )
    return products


def query_all_orders():
    orders = []
    for order in Orders.select():
        orders.append(
            {
                "id": order.id,
                "total_price": order.total_price,
                "email": order.email,
                "credit_card": order.credit_card,
                "shipping_information": order.shipping_information,
                "paid": order.paid,
                "transaction": order.transaction,
                "product": order.product,
                "shipping_price": order.shipping_price,
            }
        )
    orders.sort(key=lambda x: x["id"])
    return orders


def get_product_by_id(product_id):
    return Products.get(Products.id == product_id)


def check_product(product_id):
    return get_product_by_id(product_id).in_stock


def add_order_in_db(products_or_product):
    if isinstance(products_or_product, list):
        # If multiple products are received
        products = products_or_product
    else:
        # If only one product is received, convert it to a list
        products = [products_or_product]
    total_price = 0
    total_weight = 0
    # Calculating total price and total weight for all products
    for product_data in products:
        product = get_product_by_id(product_data["id"])
        total_price += float(product.price) * float(product_data["quantity"])
        total_weight += float(product.weight) * float(product_data["quantity"])

    shipping_price = 5 if total_weight <= 500 else 10 if total_weight <= 2000 else 25

    order = Orders.create(
        total_price=total_price,
        email="",
        credit_card="",
        shipping_information="",
        paid=False,
        transaction="",
        product=products,
        shipping_price=shipping_price,
    )
    return order.id


def get_order_by_id(order_id: int) -> Orders:
    return Orders.get(Orders.id == order_id)


def order_exist(order_id: int) -> bool:
    try:
        get_order_by_id(order_id)
        return True
    except:
        return False


def put_client_info(order_id: int, client_info: dict):
    if helpers.client_info_is_valid(client_info) == False:
        return (
            {
                "errors": {
                    "order": {
                        "code": "missing-fields",
                        "name": "Il manque un ou plusieurs champs qui sont obligatoires",
                    }
                }
            },
            422,
        )
    order_to_update = Orders.get(Orders.id == order_id)
    order_to_update.shipping_information = client_info["shipping_information"]
    order_to_update.email = client_info["email"]
    order_to_update.save()
    return {"order": client_info}, 200


def put_credit_card_info(
    order_id: int, credit_card: dict, transaction: dict, state: bool
) -> None:
    order = Orders.get(Orders.id == order_id)
    order.credit_card = credit_card
    order.transaction = transaction
    order.paid = state
    order.save()
    return


def check_paid_order(order_id: int):
    return get_order_by_id(order_id).paid
