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

CURRENCY_ERROR = f"Currency not recognized. Allowed currencies are: {', '.join(CURRENCIES)}"

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
