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
                       receipt_id TEXT NOT NULL,
                       product_id TEXT NOT NULL,
                       quantity INTEGER,
                       PRIMARY KEY (receipt_id, product_id),
                       FOREIGN KEY (receipt_id) REFERENCES receipts (id),
                       FOREIGN KEY (product_id) REFERENCES products (id)
                   )
               """)

    def create(self, item: ReceiptItem) -> ReceiptItem:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO receipt_items (
                    receipt_id, product_id, quantity
                ) VALUES (?, ?, ?)
                """,
                (
                    str(item.receipt_id),
                    str(item.product_id),
                    item.quantity,
                )
            )
            connection.commit()
            return item

    def update(self, item: ReceiptItem) -> None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE receipt_items
                SET quantity = ?
                WHERE receipt_id = ? AND product_id = ?
                """,
                (
                    item.quantity,
                    str(item.receipt_id),
                    str(item.product_id),
                )
            )
            connection.commit()

    def read(self, receipt_id: UUID, item_id: UUID) -> ReceiptItem | None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT * FROM receipt_items 
                WHERE product_id = ? AND receipt_id = ?
                """,
                (
                    str(item_id),
                    str(receipt_id),
                )
            )
            row = cursor.fetchone()
            if row:
                return ReceiptItem(
                    receipt_id=UUID(row[0]),
                    product_id=UUID(row[1]),
                    quantity=row[2]
                )
            return None

    # todo
    def read_by_receipt(self, receipt_id: UUID) -> List[ReceiptItem]:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM receipt_items WHERE receipt_id = ?",
                (str(receipt_id),)
            )
            rows = cursor.fetchall()
            print(rows)
            return [
                ReceiptItem(
                    receipt_id=UUID(row[0]),
                    product_id=UUID(row[1]),
                    quantity=row[2]
                )
                for row in rows
            ]