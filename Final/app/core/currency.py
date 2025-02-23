from dataclasses import dataclass
from enum import Enum


class Currency(str, Enum):
    GEL = "GEL"
    USD = "USD"
    EUR = "EUR"


@dataclass
class CurrencyService:
    def convert(self,
                amount: float,
                from_currency: Currency,
                to_currency: Currency) -> float:
        if from_currency == to_currency:
            return amount
    # TODO: get currencys from API