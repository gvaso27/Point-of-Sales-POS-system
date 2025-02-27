from typing import Dict, List
from uuid import UUID

from app.core.shift import ShiftItem, ShiftRepository, ShiftState


class InMemoryShiftDb(ShiftRepository):
    def __init__(self) -> None:
        self.shifts: Dict[UUID, ShiftItem] = {}

    def create(self, shift: ShiftItem) -> ShiftItem | None:
        self.shifts[shift.shift_id] = shift
        return shift

    def read(self, shift_id: UUID) -> ShiftItem | None:
        return self.shifts.get(shift_id, None)

    def update(self, shift: ShiftItem) -> None:
        if shift.shift_id in self.shifts:
            self.shifts[shift.shift_id] = shift

    def read_by_state(self, state: ShiftState) -> List[ShiftItem] | None:
        return [shift for shift in self.shifts.values() if shift.state == state]
