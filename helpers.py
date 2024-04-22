# Import des Models de l'ORM
from Models import Products, Orders

# Import des fonctions faisant des actions sur la base de données
import db

# Import des modules externes
import requests, json

# Import fonction check_queue, process_payment, cache_order depuis la file d'attente de paiement
from payment_queue import check_queue, process_payment, cache_order


def order_is_valid(order):
    if isinstance(order, list):  # Si c'est une liste de produits
        for product in order:
            if (
                not {"id", "quantity"}.issubset(product.keys())
                or int(product.get("quantity")) < 1
                or len(product) == 0
            ):
                error_response = {
                    "product": {
                        "code": "missing-fields",
                        "name": "La création d'une commande nécessite un produit",
                    }
                }
                return False, error_response

            if not db.check_product(product.get("id")):
                error_response = {
                    "product": {
                        "code": "out-of-inventory",
                        "name": "Le produit demandé n'est pas en inventaire",
                    }
                }
                return False, error_response
    else:  # Si c'est un seul produit
        if (
            not {"id", "quantity"}.issubset(order.keys())
            or int(order.get("quantity")) < 1
            or len(order) == 0
        ):
            error_response = {
                "product": {
                    "code": "missing-fields",
                    "name": "La création d'une commande nécessite un produit",
                }
            }
            return False, error_response

        if not db.check_product(order.get("id")):
            error_response = {
                "product": {
                    "code": "out-of-inventory",
                    "name": "Le produit demandé n'est pas en inventaire",
                }
            }
            return False, error_response

    return True, order


def format_order(order) -> dict:
    order = {
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
    return order


def format_product(product) -> dict:
    product = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "in_stock": product.in_stock,
        "image": product.image,
        "weight": product.weight,
    }
    return product


def format_products(products) -> list:
    list_formatted_products = []
    for i in products:
        list_formatted_products.append(format_product(i))
    return list_formatted_products


def get_amount_charged(order_id: int) -> float:
    order = db.get_order_by_id(order_id)
    return order.total_price + order.shipping_price


def client_info_is_valid(client_info) -> bool:
    required_fields = {"country", "address", "postal_code", "city", "province"}
    shipping_info = client_info.get("shipping_information", {})
    if not {"email", "shipping_information"}.issubset(
        client_info.keys()
    ) or not required_fields.issubset(shipping_info.keys()):
        return False
    return True


def check_client_information(order_id: int) -> bool:
    order = Orders.get(Orders.id == order_id)
    if not order.email and not order.shipping_information:
        return False
    return True


def check_credit_card(credit_card: dict, order_id: int):
    API = "http://dimprojetu.uqac.ca/~jgnault/shops/pay/"
    amount_charged = get_amount_charged(order_id)
    data = {"credit_card": credit_card, "amount_charged": amount_charged}
    response = requests.post(API, json=data).json()
    if "errors" in response:
        # payment_error(order_id, response, amount_charged)
        process_payment(False, order_id, credit_card, response)
        cache_order(order_id, db.get_order_by_id(order_id))
        return False
    if "transaction" in response:
        process_payment(True, order_id, credit_card, response["transaction"])
        cache_order(order_id, db.get_order_by_id(order_id))
        return True


def is_order_in_queue(order_id: int):
    return check_queue(order_id)


from worker import redis_db


def get_order_from_cache(order_id: int) -> tuple[bool, dict | None]:
    db = redis_db()
    cached_order_data = db.get(f"order:{order_id}")
    if cached_order_data:
        return True, json.loads(cached_order_data)
    return False, None


def print_cache() -> None:
    db = redis_db()
    for key in db.scan_iter("order:*"):
        value = db.get(key)
        if value is not None:
            print(bytes(value).decode("utf-8"))
