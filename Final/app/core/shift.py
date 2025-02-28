from asyncio import Protocol
from dataclasses import dataclass
from enum import Enum
from typing import List
from uuid import UUID, uuid4


class ShiftState(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


@dataclass
class ShiftItem:
    shift_id: UUID
    state: ShiftState


class ShiftRepository(Protocol):
    def create(self, receipt: ShiftItem) -> ShiftItem | None:
        pass

    def read(self, receipt_id: UUID) -> ShiftItem | None:
        pass

    def update(self, receipt: ShiftItem) -> None:
        pass

    def read_by_state(self, state: ShiftState) -> List[ShiftItem] | None:
        pass


@dataclass
class ShiftService:
    shift_repo: ShiftRepository

    def __init__(self, shift_repo: ShiftRepository) -> None:
        self.shift_repo = shift_repo
        pass

    def create(self) -> UUID:
        open_shifts = self.shift_repo.read_by_state(ShiftState.OPEN)
        if open_shifts:
            raise ValueError(
                "An open shift already exists. Close it before creating a new one."
            )

        shift_id = uuid4()
        shift = ShiftItem(shift_id=shift_id, state=ShiftState.OPEN)
        self.shift_repo.create(shift)
        return shift_id

    def state(self, shift_id: UUID) -> ShiftState:
        shift = self.shift_repo.read(shift_id)
        if not shift:
            raise ValueError(f"Shift with ID {shift_id} not found")
        return shift.state

    def close(self, shift_id: UUID) -> None:
        shift = self.shift_repo.read(shift_id)
        if not shift:
            raise ValueError(f"Shift with ID {shift_id} not found")

        updated_shift = ShiftItem(shift_id=shift.shift_id, state=ShiftState.CLOSED)
        self.shift_repo.update(updated_shift)

    def get_open_shift(self) -> ShiftItem | None:
        open_shifts = self.shift_repo.read_by_state(ShiftState.OPEN)
        if open_shifts:
            return open_shifts[0]
        return None
