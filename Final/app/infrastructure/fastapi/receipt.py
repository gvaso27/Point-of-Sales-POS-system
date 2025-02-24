from typing import Any, no_type_check
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.currency import Currency
from app.core.product import ProductService
from app.core.receipt import (
    PaymentRequest,
    QuoteRequest,
    ReceiptService,
)
from app.core.receipt_item import AddItemRequest
from app.infrastructure.fastapi.dependables import (
    CurrencyServiceDependable,
    ProductRepositoryDependable,
    ReceiptItemRepositoryDependable,
    ReceiptRepositoryDependable,
)

receipt_api: APIRouter = APIRouter()


@receipt_api.post("/receipts", status_code=201)
@no_type_check
def create_receipt(
        receipts: ReceiptRepositoryDependable,
        receipt_items: ReceiptItemRepositoryDependable,
        currency_service: CurrencyServiceDependable
) -> dict[str, Any]:
    try:
        service = ReceiptService(receipts, receipt_items, currency_service)
        receipt_id = service.create()
        return {"receipt_id": receipt_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": {"message": str(e)}})


@receipt_api.post("/receipts/{receipt_id}/products")
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


@receipt_api.post("/receipts/{receipt_id}/calculate")
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


@receipt_api.post("/receipts/{receipt_id}/quotes")
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


@receipt_api.post("/receipts/{receipt_id}/close")
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
        currency: Currency = Currency.GEL
) -> dict[str, Any]:
    try:
        service = ReceiptService(receipts, receipt_items, currency_service)
        receipt = service.get_receipt(receipt_id, currency)
        items = service.get_receipt_items(receipt_id, currency)

        payment_info = {}
        if receipt.payment_amount and receipt.payment_currency:
            payment_info = {
                "payment_amount": receipt.payment_amount,
                "payment_currency": receipt.payment_currency.value
            }

        return {
            "receipt": {
                "id": receipt.id,
                "state": receipt.state,
                "items": [
                    {
                        "name": item.product_name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "total": item.total,
                        "discount": item.discount
                    }
                    for item in items
                ],
                "subtotal": receipt.subtotal,
                "total_discount": receipt.total_discount,
                "total": receipt.total,
                "savings": receipt.savings,
                "currency": currency.value,
                **payment_info
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"error": {"message": str(e)}})


@receipt_api.post("/receipts/{receipt_id}/payments")
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