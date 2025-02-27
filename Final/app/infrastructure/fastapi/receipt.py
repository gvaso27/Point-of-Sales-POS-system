from typing import Any, no_type_check
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.currency import Currency
from app.core.product import ProductService
from app.core.receipt import (
    PaymentRequest,
    QuoteRequest,
    ReceiptService, GetReceiptResponse, ReceiptProduct,
)
from app.core.receipt_item import AddItemRequest
from app.infrastructure.fastapi.dependables import (
    CurrencyServiceDependable,
    ProductRepositoryDependable,
    ReceiptItemRepositoryDependable,
    ReceiptRepositoryDependable, ShiftServiceDependable,
)

receipt_api: APIRouter = APIRouter()


@receipt_api.post("/newReceipt", status_code=201)
@no_type_check
def create_receipt(
        receipts: ReceiptRepositoryDependable,
        receipt_items: ReceiptItemRepositoryDependable,
        currency_service: CurrencyServiceDependable,
        shift_service: ShiftServiceDependable
) -> dict[str, Any]:
    try:
        service = ReceiptService(receipts, receipt_items, shift_service, currency_service)
        receipt_id = service.create()
        return {"receipt_id": receipt_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": {"message": str(e)}})


@receipt_api.post("/receipts/addItem/{receipt_id}")
@no_type_check
def add_item(
        receipt_id: UUID,
        request: AddItemRequest,
        receipts: ReceiptRepositoryDependable,
        receipt_items: ReceiptItemRepositoryDependable,
        currency_service: CurrencyServiceDependable,
        products: ProductRepositoryDependable
) -> None:
    try:
        product = ProductService(products).read(request.product_id)
        service = ReceiptService(receipts, receipt_items, currency_service)
        service.add_item(receipt_id, request, product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": {"message": str(e)}})


@receipt_api.get("/receipts/calculate/{receipt_id}")
@no_type_check
def calculate_total(
        receipt_id: UUID,
        receipts: ReceiptRepositoryDependable,
        receipt_items: ReceiptItemRepositoryDependable,
        currency_service: CurrencyServiceDependable
) -> dict[str, float]:
    try:
        service = ReceiptService(receipts, receipt_items, currency_service)
        total = service.calculate_total(receipt_id)
        return {"total": total}
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": {"message": str(e)}})


@receipt_api.get("/receipts/quotes/{receipt_id}")
@no_type_check
def get_quote(
        receipt_id: UUID,
        request: QuoteRequest,
        receipts: ReceiptRepositoryDependable,
        receipt_items: ReceiptItemRepositoryDependable,
        currency_service: CurrencyServiceDependable
) -> dict[str, Any]:
    try:
        service = ReceiptService(receipts, receipt_items, currency_service)
        quote = service.get_quote(receipt_id, request.currency)
        return {
            "subtotal": quote.subtotal,
            "total_discount": quote.total_discount,
            "total": quote.total,
            "currency": quote.currency.value
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": {"message": str(e)}})


@receipt_api.post("/receipts/close/{receipt_id}")
@no_type_check
def close_receipt(
        receipt_id: UUID,
        receipts: ReceiptRepositoryDependable,
        receipt_items: ReceiptItemRepositoryDependable,
        currency_service: CurrencyServiceDependable
) -> None:
    try:
        service = ReceiptService(receipts, receipt_items, currency_service)
        service.close_receipt(receipt_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": {"message": str(e)}})


@receipt_api.get("/receipts/{receipt_id}")
@no_type_check
def get_receipt(
        receipt_id: UUID,
        receipts: ReceiptRepositoryDependable,
        receipt_items: ReceiptItemRepositoryDependable,
        currency_service: CurrencyServiceDependable,
        products: ProductRepositoryDependable,
        currency: Currency = Currency.GEL
) -> GetReceiptResponse:
    try:
        service = ReceiptService(receipts, receipt_items, currency_service)
        receipt = service.get_receipt(receipt_id, currency)
        items = service.get_receipt_items(receipt_id, currency)

        receipt_items = []
        for item in items:
            cur_product = products.read(item.product_id)
            receipt_items.append(ReceiptProduct(
                id=cur_product.id,
                name=cur_product.name,
                price=cur_product.price,
                quantity=item.quantity
            ))

        return GetReceiptResponse(
            id=receipt.id,
            state=receipt.state.value,
            subtotal=receipt.subtotal,
            total_discount=receipt.total_discount,
            total=receipt.total,
            savings=receipt.savings,
            currency=receipt.payment_currency,
            items=receipt_items
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"error": {"message": str(e)}})


@receipt_api.post("/receipts/pay/{receipt_id}")
@no_type_check
def process_payment(
        receipt_id: UUID,
        payment: PaymentRequest,
        receipts: ReceiptRepositoryDependable,
        receipt_items: ReceiptItemRepositoryDependable,
        currency_service: CurrencyServiceDependable
) -> None:
    try:
        service = ReceiptService(receipts, receipt_items, currency_service)
        service.process_payment(receipt_id, payment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": {"message": str(e)}})
