import click
import peewee, pg8000, json, time

# Flask
from flask import Flask, render_template, request, jsonify, redirect

# Models
from Models import Products, Orders

# Helpers, db
import helpers, db


# App
app = Flask(__name__)


# CLI commands
cmd = {
    "init-db": "Create the database tables",
    "drop-db": "Drop the database tables",
    "flush": "Drop and recreate the database tables",
    "worker": """Start a worker to process payment tasks.
        Default number of workers is 1.
        Can receive an optional argument to start more workers. --number 2 for example.""",
    "cache": "Print the cache",
}


@app.cli.command("help")
def help():
    """List all available commands"""
    for key, value in cmd.items():
        print(f"{key}: {value}")


@app.cli.command("init-db")
def initdb():
    """Create the database tables"""
    db.create_tables()


@app.cli.command("drop-db")
def dropdb():
    """Drop the database tables"""
    db.drop_tables()


@app.cli.command("flush")
def flushdb():
    """Drop and recreate the database tables"""
    db.flush()


@app.cli.command("worker")
@click.option("--number", default=1, help="Number of workers to start")
def start_worker(number: int):
    """Start a worker to process payment tasks.
    Default number of workers is 1.
    Can receive an optional argument to start more workers. --number=2 for example."""
    from worker import conn, Connection, Worker, Queue

    print("Number of workers: ", number)
    with Connection(conn):
        worker = Worker(Queue("payment"), connection=conn)
        for _ in range(number):
            worker.work()


@app.cli.command("cache")
def cache():
    """Print the cache"""
    return helpers.print_cache()


# Routes
# GET /products
@app.route("/", methods=["GET"])
def get_products():
    return jsonify({"products": db.query_all_products()}), 200


# GET /product/<id>
@app.route("/products/<int:product_id>", methods=["GET"])
def get_product_by_id(product_id):
    return (
        jsonify({"product:": helpers.format_product(db.get_product_by_id(product_id))}),
        200,
    )


# POST /order
@app.route("/order", methods=["POST"])
def order():
    req = request.json
    if "products" in req:
        is_valid, error = helpers.order_is_valid(req["products"])
        id = db.add_order_in_db(req["products"])
    elif "product" in req:
        is_valid, error = helpers.order_is_valid(req["product"])
        id = db.add_order_in_db(req["product"])
    else:
        return jsonify("Aucun produit n'a été trouvé..."), 404
    if is_valid == False:
        return jsonify(errors=error), 422

    return redirect("/order/" + str(id))


# GET /order/<order_id>
@app.route("/order/<int:order_id>", methods=["GET"])
def get_order(order_id):
    if helpers.is_order_in_queue(order_id):
        return (jsonify({}), 202)
    # Vérifie si les données de commande sont en cache dans Redis
    _, cached_order_data = helpers.get_order_from_cache(order_id)
    if _:
        print("Order data from cache")
        return jsonify({"order": cached_order_data}), 200
    print("Order data from db")
    formatted_order = helpers.format_order(db.get_order_by_id(order_id))
    return jsonify({"order": formatted_order}), 200


# PUT /order/<order_id>
@app.route("/order/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    if "order" in request.json:
        return put_client_info(order_id, request.json["order"])
    elif "credit_card" in request.json:
        return pay_order(order_id, request.json["credit_card"])


# mettre à jour les informations du client
def put_client_info(order_id, req):
    if db.order_exist(order_id) == False:
        return jsonify("Cette commande n'existe pas..."), 404
    client_info, code = db.put_client_info(order_id, req)
    return jsonify(client_info), code


# mettre à jour les informations de payement d'une commande
def pay_order(order_id: int, credit_card: dict):
    if not helpers.check_client_information(order_id):
        return (
            jsonify(
                {
                    "errors": {
                        "order": {
                            "code": "missing-fields",
                            "name": "Les informations du client sont nécessaire avant d'appliquer une carte de crédit",
                        }
                    }
                }
            ),
            422,
        )
    if db.check_paid_order(order_id):
        return (
            jsonify(
                {
                    "errors": {
                        "order": {
                            "code": "already-paid",
                            "name": "La commande a déjà été payée.",
                        }
                    }
                }
            ),
            422,
        )
    if not helpers.check_credit_card(credit_card, order_id):
        return (
            jsonify(
                {
                    "credit_card": {
                        "code": "card-declined",
                        "name": "La carte de crédit a été déclinée.",
                    }
                }
            ),
            422,
        )
    else:
        return (
            jsonify({"order": helpers.format_order(db.get_order_by_id(order_id))}),
            200,
        )


def put_credit_card_info(order_id, credit_card):
    return jsonify(helpers.check_credit_card(credit_card, order_id))


## Routes pour l'interface Web ;


# route pour afficher les produits version web
@app.route("/home", methods=["GET"])
def home():
    return render_template("home.html", products=db.query_all_products())


# route pour faire une commande ;
@app.route("/orders", methods=["GET"])
def orders():
    return render_template("orders.html", products=db.query_all_products())


# Route pour lister toutes les commandes
@app.route("/orders/list", methods=["GET"])
def list_orders():
    return render_template("list_orders.html", orders=db.query_all_orders())


# Route pour completer une commande
# GET /order/<order_id>/complete
@app.route("/order/<int:order_id>/complete", methods=["GET"])
def complete_order(order_id):
    return render_template(
        "complete_order.html",
        order=db.get_order_by_id(order_id),
        product_info=db.get_product_by_id(order_id),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
