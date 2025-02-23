import sqlite3
from typing import List
from uuid import UUID

from app.core.receipt import Receipt, ReceiptRepository, ReceiptState


class ReceiptDb(ReceiptRepository):
    def __init__(self, db_path: str = "./store.db"):
        self.db_path = db_path
        self.up()

    def up(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS receipts (
                    id TEXT PRIMARY KEY,
                    shift_id TEXT,
                    state TEXT,
                    created_at TIMESTAMP,
                    subtotal FLOAT,
                    total_discount FLOAT,
                    payment_amount FLOAT,
                    payment_currency TEXT
                )
            """)

    def create(self, receipt: Receipt) -> Receipt:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO receipts (
                    id, shift_id, state, created_at, 
                    subtotal, total_discount
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(receipt.id), str(receipt.shift_id),
                    receipt.state.value, receipt.created_at,
                    receipt.subtotal, receipt.total_discount
                )
            )
            connection.commit()
            return receipt

    def read(self, receipt_id: UUID) -> Receipt | None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM receipts WHERE id = ?",
                (str(receipt_id),)
            )
            row = cursor.fetchone()
            if row:
                return Receipt(
                    id=UUID(row[0]),
                    shift_id=UUID(row[1]),
                    state=ReceiptState(row[2]),
                    created_at=row[3],
                    subtotal=row[4],
                    total_discount=row[5]
                )
            return None

    def update(self, receipt: Receipt) -> None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE receipts 
                SET state = ?,
                    subtotal = ?,
                    total_discount = ?
                WHERE id = ?
                """,
                (
                    receipt.state.value,
                    receipt.subtotal,
                    receipt.total_discount,
                    str(receipt.id)
                )
            )
            connection.commit()

    def read_by_shift(self, shift_id: UUID) -> List[Receipt]:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM receipts WHERE shift_id = ?",
                (str(shift_id),)
            )
            rows = cursor.fetchall()
            return [
                Receipt(
                    id=UUID(row[0]),
                    shift_id=UUID(row[1]),
                    state=ReceiptState(row[2]),
                    created_at=row[3],
                    subtotal=row[4],
                    total_discount=row[5]
                )
                for row in rows
            ]
