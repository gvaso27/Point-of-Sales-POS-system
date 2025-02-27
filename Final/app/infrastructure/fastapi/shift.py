from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.report import XReport, ReportService, ReportRevenue
from app.core.shift import ShiftService
from app.infrastructure.fastapi.dependables import ShiftRepositoryDependable, ReceiptRepositoryDependable, \
    ReceiptItemRepositoryDependable, ShiftServiceDependable

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


@shift_api.get("/shifts/x-reports")
def get_x_report(receipts: ReceiptRepositoryDependable,
                 receipt_items: ReceiptItemRepositoryDependable,
                 shifts: ShiftServiceDependable) -> XReport:
    try:
        service = ReportService(receipts, receipt_items, shifts)
        return service.generate_x_report()
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"error": {"message": str(e)}})


@shift_api.get("/shifts/z-reports")
def get_y_report(receipts: ReceiptRepositoryDependable,
                 receipt_items: ReceiptItemRepositoryDependable,
                 shifts: ShiftServiceDependable) -> list[ReportRevenue]:
    try:
        service = ReportService(receipts, receipt_items, shifts)
        return service.generate_z_report()
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"error": {"message": str(e)}})
