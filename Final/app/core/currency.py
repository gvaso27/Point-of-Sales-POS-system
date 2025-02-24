from dataclasses import dataclass
from enum import Enum
from typing import Dict

import requests


class Currency(str, Enum):
    GEL = "GEL"
    USD = "USD"
    EUR = "EUR"


@dataclass
class CurrencyService:
    _rates: Dict[str, float] = None

    def __init__(self):
        self._rates = {}
        self._update_rates()

    def _update_rates(self) -> None:
        try:
            response = requests.get(
                "https://open.er-api.com/v6/latest/GEL"
            )
            data = response.json()

            if data["result"] == "success":
                self._rates[Currency.GEL.value] = 1.0
                self._rates[Currency.USD.value] = data["rates"]["USD"]
                self._rates[Currency.EUR.value] = data["rates"]["EUR"]
        except Exception:
            self._rates = {
                Currency.GEL.value: 1.0,
                Currency.USD.value: 0.37,
                Currency.EUR.value: 0.34,
            }

    def convert(self,
                amount: float,
                from_currency: Currency,
                to_currency: Currency) -> float:

        if from_currency == to_currency:
            return amount
        if not self._rates:
            self._update_rates()

        amount_in_gel = amount
        if from_currency != Currency.GEL:
            amount_in_gel = amount / self._rates[from_currency.value]
        if to_currency == Currency.GEL:
            return round(amount_in_gel, 2)

        return round(amount_in_gel * self._rates[to_currency.value], 2)
