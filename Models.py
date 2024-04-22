from peewee import (
    PostgresqlDatabase,
    Model,
    AutoField,
    CharField,
    TextField,
    IntegerField,
    FloatField,
    BooleanField,
)
from playhouse.postgres_ext import JSONField
import os, socket
from dotenv import load_dotenv

load_dotenv()


def get_ip_from_dns_name(dns_name: str) -> str | None:
    """Permet de fournir le nom du service dans la commande docker run, et de récupérer l'adresse IP associée."""
    try:
        ip = socket.gethostbyname(dns_name)
        return ip
    except:
        return None


# Configuration de la base de données PostgreSQL avec Peewee

pg_db = PostgresqlDatabase(
    os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=get_ip_from_dns_name(os.getenv("DB_HOST", default="db")),
    port=os.getenv("DB_PORT", default=5432),
)


# Configuration des models
class BaseModel(Model):
    class Meta:
        database = pg_db


class Products(Model):
    id = AutoField(primary_key=True)
    name = CharField()
    type = CharField()
    description = TextField()
    image = CharField()  # JSP si BLOB ou pas donc pour l'instant VARCHAR
    height = IntegerField()
    weight = IntegerField()
    price = FloatField()
    in_stock = BooleanField()

    class Meta:
        database = pg_db


class Orders(Model):
    id = AutoField(primary_key=True)
    total_price = FloatField()
    email = CharField()
    credit_card = JSONField()
    shipping_information = JSONField()
    paid = BooleanField()
    transaction = JSONField()
    product = JSONField()
    shipping_price = IntegerField()

    class Meta:
        database = pg_db


Products.create_table()
Orders.create_table()
