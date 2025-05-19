import sqlite3
from typing import List
from uuid import UUID

from app.core.Models.product import Product


class ProductDb(object):
    def __init__(self, db_path: str = "./store.db"):
        self.db_path = db_path
        self.up()

    def up(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            create_table_query = """
                        CREATE TABLE IF NOT EXISTS products (
                            id TEXT,
                            name TEXT,
                            price FLOAT
                        )
                    """
            cursor.execute(create_table_query)

    def clear(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()

            truncate_products_query = """
                DELETE FROM products;
            """

            cursor.execute(truncate_products_query)
            connection.commit()

    def read(self, product_id: UUID) -> Product | None:
        select_query = """
            SELECT name, price, id FROM products WHERE id = ?;
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(select_query, (str(product_id),))
            row = cursor.fetchone()
            if row:
                return Product(
                    name=row[0],
                    price=row[1],
                    id=row[2],
                )
        return None

    def add(self, product: Product) -> Product:
        insert_query = """
            INSERT INTO products (id, name, price)
            VALUES (?, ?, ?);
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(insert_query, (str(product.id), product.name, product.price))
            connection.commit()
            return product

    def find_by_name(self, name: str) -> Product | None:
        select_query = """
            SELECT name, price, id FROM products WHERE name = ?;
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(select_query, (name,))
            row = cursor.fetchone()
            if row:
                return Product(
                    name=row[0],
                    price=row[1],
                    id=row[2],
                )
            return None

    def read_all(self) -> List[Product]:
        select_query = """
            SELECT name, price, id FROM products;
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(select_query)
            rows = cursor.fetchall()
            return [
                Product(
                    name=row[0],
                    price=row[1],
                    id=row[2],
                )
                for row in rows
            ]

    def update(self, product: Product) -> None:
        update_query = """
            UPDATE products
            SET name = ?,
                price = ?
            WHERE id = ?
        """
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(update_query, (product.name, product.price, str(product.id)))
            connection.commit()
