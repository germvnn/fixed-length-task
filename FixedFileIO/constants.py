HEADER_SLICES = {
        'Field ID': (0, 2),
        'Name': (2, 30),
        'Surname': (30, 60),
        'Patronymic': (60, 90),
        'Address': (90, 120)
    }

TRANSACTIONS_SLICES = {
        'Field ID': (0, 2),
        'Counter': (2, 8),
        'Amount': (8, 20),
        'Currency': (20, 23),
        'Reserved': (23, 120)
    }

FOOTER_SLICES = {
        'Field ID': (0, 2),
        'Total Counter': (2, 8),
        'Control sum': (8, 20),
        'Reserved': (20, 120)
    }

CURRENCIES = [
    "USD", "EUR", "JPY", "GBP", "AUD",
    "CAD", "CHF", "CNY", "SEK", "NZD",
    "MXN", "SGD", "HKD", "NOK", "KRW",
    "TRY", "RUB", "INR", "BRL", "ZAR",
    "DKK", "PLN", "THB", "IDR", "HUF",
    "CZK", "ILS", "CLP", "PHP", "AED",
    "COP", "SAR", "MYR", "RON", "PEN",
    "VND", "NGN", "BDT", "PKR", "QAR"
]


FIELD_TYPES = {
    "Field ID": str,
    "Name": str,
    "Surname": str,
    "Patronymic": str,
    "Address": str,
    "Counter": str,
    "Amount": float,
    "Currency": str,
    "Total Counter": int,
    "Control sum": int
}

HEADER_FIELDS = {"Field ID", "Name", "Surname", "Patronymic", "Address"}
TRANSACTION_FIELDS = {"Field ID", "Counter", "Amount", "Currency"}
FOOTER_FIELDS = {"Total Counter", "Control sum"}

AUTO_FIELDS = {"Field ID", "Counter", "Total Counter", "Control sum"}

CURRENCY_ERROR = f"Currency not recognized. Allowed currencies are: {', '.join(CURRENCIES)}"
