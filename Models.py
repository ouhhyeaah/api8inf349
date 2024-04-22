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
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration de la base de données PostgreSQL avec Peewee
DATABASE = "api8inf349"
pg_db = PostgresqlDatabase(
    DATABASE,
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
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
