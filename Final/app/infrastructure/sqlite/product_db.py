import sqlite3
from uuid import UUID

from app.core.product import Product


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

    def read(self, product_id: UUID) -> Product:
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
            else:
                raise Exception(f"product with {product_id} does not exist")
