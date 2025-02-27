from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.shift import ShiftService
from app.infrastructure.fastapi.dependables import ShiftRepositoryDependable

shift_api: APIRouter = APIRouter()


@shift_api.post("/shifts/open", status_code=201)
def open_shift(shifts: ShiftRepositoryDependable) -> dict[str, Any]:
    try:
        service = ShiftService(shifts)
        shift_id = service.create()
        return {"shift_id": shift_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": {"message": str(e)}})


@shift_api.get("/shifts/state/{shift_id}")
def get_shift_state(shift_id: UUID, shifts: ShiftRepositoryDependable) -> dict[str, str]:
    try:
        service = ShiftService(shifts)
        state = service.state(shift_id)
        return {"shift_id": str(shift_id), "state": state.value}
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"error": {"message": str(e)}})


@shift_api.post("/shifts/close/{shift_id}")
def close_shift(shift_id: UUID, shifts: ShiftRepositoryDependable) -> None:
    try:
        service = ShiftService(shifts)
        service.close(shift_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": {"message": str(e)}})


@shift_api.get("/shifts/x-reports/{shift_id}")
def get_x_report(shift_id: UUID, shifts: ShiftRepositoryDependable) -> dict[str, Any]:
    try:
        service = ShiftService(shifts)
        report = service.get_x_report(shift_id)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"error": {"message": str(e)}})


@shift_api.get("/shifts/y-reports/{shift_id}")
def get_y_report(shift_id: UUID, shifts: ShiftRepositoryDependable) -> dict[str, Any]:
    try:
        service = ShiftService(shifts)
        report = service.get_y_report(shift_id)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"error": {"message": str(e)}})
