import sqlite3
from typing import List, Optional
from uuid import UUID
from app.core.shift import ShiftItem, ShiftRepository, ShiftState


class ShiftDb(ShiftRepository):
    def __init__(self, db_path: str = "./store.db"):
        self.db_path = db_path
        self.up()

    def up(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shifts (
                    shift_id TEXT PRIMARY KEY,
                    state TEXT
                )
            """)

    def create(self, shift: ShiftItem) -> ShiftItem:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO shifts (shift_id, state) VALUES (?, ?)
                """,
                (str(shift.shift_id), shift.state.value)
            )
            connection.commit()
            return shift

    def read(self, shift_id: UUID) -> Optional[ShiftItem]:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM shifts WHERE shift_id = ?",
                (str(shift_id),)
            )
            row = cursor.fetchone()
            if row:
                return ShiftItem(
                    shift_id=UUID(row['shift_id']),
                    state=ShiftState(row['state'])
                )
            return None

    def update(self, shift: ShiftItem) -> None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE shifts
                SET state = ?
                WHERE shift_id = ?
                """,
                (shift.state.value, str(shift.shift_id))
            )
            connection.commit()

    def read_by_state(self, state: ShiftState) -> List[ShiftItem]:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM shifts WHERE state = ?",
                (state.value,)
            )
            rows = cursor.fetchall()
            shifts = []
            for row in rows:
                shifts.append(
                    ShiftItem(
                        shift_id=UUID(row['shift_id']),
                        state=ShiftState(row['state'])
                    )
                )
            return shifts
