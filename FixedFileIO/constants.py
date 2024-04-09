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