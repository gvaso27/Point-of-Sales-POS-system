import sqlite3
from typing import List
from uuid import UUID

from app.core.receipt_item import ReceiptItem, ReceiptItemRepository


class ReceiptItemDb(ReceiptItemRepository):
    def __init__(self, db_path: str = "./store.db"):
        self.db_path = db_path
        self.up()

    def up(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS receipt_items (
                    id TEXT PRIMARY KEY,
                    receipt_id TEXT,
                    product_id TEXT,
                    product_name TEXT,
                    quantity INTEGER,
                    unit_price FLOAT,
                    discount FLOAT,
                    FOREIGN KEY (receipt_id) REFERENCES receipts (id)
                )
            """)

    def create(self, item: ReceiptItem) -> ReceiptItem:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO receipt_items (
                    id, receipt_id, product_id, quantity,
                    unit_price, discount
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(item.id), str(item.receipt_id),
                    str(item.product_id), item.quantity,
                    item.unit_price, item.discount
                )
            )
            connection.commit()
            return item

    def read(self, item_id: UUID) -> ReceiptItem | None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM receipt_items WHERE id = ?",
                (str(item_id),)
            )
            row = cursor.fetchone()
            if row:
                return ReceiptItem(
                    id=UUID(row[0]),
                    receipt_id=UUID(row[1]),
                    product_id=UUID(row[2]),
                    quantity=row[3],
                    unit_price=row[4],
                    discount=row[5]
                )
            return None

    def read_by_receipt(self, receipt_id: UUID) -> List[ReceiptItem]:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM receipt_items WHERE receipt_id = ?",
                (str(receipt_id),)
            )
            rows = cursor.fetchall()
            return [
                ReceiptItem(
                    id=UUID(row[0]),
                    receipt_id=UUID(row[1]),
                    product_id=UUID(row[2]),
                    quantity=row[3],
                    unit_price=row[4],
                    discount=row[5]
                )
                for row in rows
            ]

    def delete_by_receipt(self, receipt_id: UUID) -> None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM receipt_items WHERE receipt_id = ?",
                (str(receipt_id),)
            )
            connection.commit()
