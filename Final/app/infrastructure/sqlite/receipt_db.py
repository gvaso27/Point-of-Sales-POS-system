import sqlite3
from typing import List
from uuid import UUID

from app.core.currency import Currency
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
                    payment_currency TEXT,
                    FOREIGN KEY (shift_id) REFERENCES shifts (shift_id)
                )
            """)

    def create(self, receipt: Receipt) -> Receipt:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO receipts (
                    id, shift_id, state, created_at, 
                    subtotal, total_discount, payment_amount, payment_currency
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(receipt.id), str(receipt.shift_id),
                    receipt.state.value, receipt.created_at,
                    receipt.subtotal, receipt.total_discount,
                    receipt.payment_amount,
                    receipt.payment_currency.value if receipt.payment_currency else None
                )
            )
            connection.commit()
            return receipt

    def read(self, receipt_id: UUID) -> Receipt | None:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM receipts WHERE id = ?",
                (str(receipt_id),)
            )
            row = cursor.fetchone()
            if row:
                payment_currency = None
                if row['payment_currency']:
                    payment_currency = Currency(row['payment_currency'])

                return Receipt(
                    id=UUID(row['id']),
                    shift_id=UUID(row['shift_id']),
                    state=ReceiptState(row['state']),
                    created_at=row['created_at'],
                    subtotal=row['subtotal'],
                    total_discount=row['total_discount'],
                    payment_amount=row['payment_amount'],
                    payment_currency=payment_currency
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
                    total_discount = ?,
                    payment_amount = ?,
                    payment_currency = ?
                WHERE id = ?
                """,
                (
                    receipt.state.value,
                    receipt.subtotal,
                    receipt.total_discount,
                    receipt.payment_amount,
                    receipt.payment_currency.value
                    if receipt.payment_currency
                    else None,
                    str(receipt.id)
                )
            )
            connection.commit()

    def read_by_shift(self, shift_id: UUID) -> List[Receipt]:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM receipts WHERE shift_id = ?",
                (str(shift_id),)
            )
            rows = cursor.fetchall()
            receipts = []

            for row in rows:
                payment_currency = None
                if row['payment_currency']:
                    payment_currency = Currency(row['payment_currency'])

                receipt = Receipt(
                    id=UUID(row['id']),
                    shift_id=UUID(row['shift_id']),
                    state=ReceiptState(row['state']),
                    created_at=row['created_at'],
                    subtotal=row['subtotal'],
                    total_discount=row['total_discount'],
                    payment_amount=row['payment_amount'],
                    payment_currency=payment_currency
                )
                receipts.append(receipt)
        return receipts

    def get_all(self) -> List[Receipt]:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM receipts")
            rows = cursor.fetchall()
            receipts = []
            for row in rows:
                payment_currency = None
                if row['payment_currency']:
                    payment_currency = Currency(row['payment_currency'])

                receipt = Receipt(
                    id=UUID(row['id']),
                    shift_id=UUID(row['shift_id']),
                    state=ReceiptState(row['state']),
                    created_at=row['created_at'],
                    subtotal=row['subtotal'],
                    total_discount=row['total_discount'],
                    payment_amount=row['payment_amount'],
                    payment_currency=payment_currency
                )
                receipts.append(receipt)
        return receipts
