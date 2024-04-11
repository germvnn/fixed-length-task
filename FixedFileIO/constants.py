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

MAX_LENGTHS = {
    'Field ID': HEADER_SLICES['Field ID'][1] - HEADER_SLICES['Field ID'][0],
    'Name': HEADER_SLICES['Name'][1] - HEADER_SLICES['Name'][0],
    'Surname': HEADER_SLICES['Surname'][1] - HEADER_SLICES['Surname'][0],
    'Patronymic': HEADER_SLICES['Patronymic'][1] - HEADER_SLICES['Patronymic'][0],
    'Address': HEADER_SLICES['Address'][1] - HEADER_SLICES['Address'][0],
    'Counter': TRANSACTIONS_SLICES['Counter'][1] - TRANSACTIONS_SLICES['Counter'][0],
    'Amount': TRANSACTIONS_SLICES['Amount'][1] - TRANSACTIONS_SLICES['Amount'][0],
    'Currency': TRANSACTIONS_SLICES['Currency'][1] - TRANSACTIONS_SLICES['Currency'][0],
    'Total Counter': FOOTER_SLICES['Total Counter'][1] - FOOTER_SLICES['Total Counter'][0],
    'Control sum': FOOTER_SLICES['Control sum'][1] - FOOTER_SLICES['Control sum'][0]
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
    "Amount": int,
    "Currency": str,
    "Total Counter": int,
    "Control sum": int
}

# Address can have digits. Currencies are fixed
FIELD_VALIDATIONS = {
    'Field ID': str.isdigit,
    'Name': str.isalpha,
    'Surname': str.isalpha,
    'Patronymic': str.isalpha,
    'Amount': str.isdigit,
    'Counter': str.isdigit,
    'Total Counter': str.isdigit,
    'Control sum': str.isdigit,
}

HEADER_FIELDS = {"Field ID", "Name", "Surname", "Patronymic", "Address"}
TRANSACTION_FIELDS = {"Field ID", "Counter", "Amount", "Currency"}
FOOTER_FIELDS = {"Total Counter", "Control sum"}

AUTO_FIELDS = {"Field ID", "Counter", "Total Counter", "Control sum"}

CURRENCY_ERROR = f"Currency not recognized. Allowed currencies are: {', '.join(CURRENCIES)}"
