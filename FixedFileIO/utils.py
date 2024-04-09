from . import constants as const
import re


class TransactionLimitError(Exception):
    """Exception raised when the maximum
     number of transactions is exceeded."""
    def __init__(self, limit, message="Too many transactions"):
        self.limit = limit
        self.message = message
        super().__init__(f"{message}: {limit}")


def get_values_as_dict(line, slices):
    values = {}
    for key, (start, end) in slices.items():
        values[key] = line[start:end].strip()
    return values


class Validation:
    def __init__(self, filepath):
        self.filepath = filepath

    @staticmethod
    def _validate_header(line):
        slices = const.HEADER_SLICES

        field_id = line[slices['Field ID'][0]:slices['Field ID'][1]]
        name = line[slices['Name'][0]:slices['Name'][1]].strip()
        surname = line[slices['Surname'][0]:slices['Surname'][1]].strip()
        patronymic = line[slices['Patronymic'][0]:slices['Patronymic'][1]].strip()
        address = line[slices['Address'][0]:slices['Address'][1]].strip()

        # Field ID validation
        if not re.match(r'^01$', field_id):
            return False, "Invalid Field ID in header."

        # Name, Surname, Patronymic validation
        for item in [name, surname, patronymic]:
            if not re.match(r'^[A-Za-z\s]+$', item):
                return False, f"{item} is invalid"

        # Address validation
        if not re.match(r'^[\w\s,.]+$', address):
            return False, "Invalid Address in header."

        return True, "Header is valid."

    @staticmethod
    def _validate_transactions(lines):
        slices = const.TRANSACTIONS_SLICES

        for line in lines:
            field_id = line[slices['Field ID'][0]:slices['Field ID'][1]]
            counter = line[slices['Counter'][0]:slices['Counter'][1]]
            amount = line[slices['Amount'][0]:slices['Amount'][1]]
            currency = line[slices['Currency'][0]:slices['Currency'][1]]

            # Field ID validation
            if not re.match(r'^02$', field_id):
                return False, "Invalid Field ID in transaction"

            # Counter validation
            if not re.match(r'^\d{6}$', counter):
                return False, "Counter format is not correct."

            # Amount validation
            if not re.match(r'^\d{12}$', amount):
                return False, "Amount format is not correct."

            # Currency validation
            if currency not in const.CURRENCIES:
                return False, f"Invalid currency '{currency}' in transaction."

        return True, "All transactions are valid"

    @staticmethod
    def _validate_footer(line, num_transactions, total_amount):
        slices = const.FOOTER_SLICES

        field_id = line[slices['Field ID'][0]:slices['Field ID'][1]]
        total_counter = line[slices['Total Counter'][0]:slices['Total Counter'][1]]
        control_sum = line[slices['Control sum'][0]:slices['Control sum'][1]]

        # Field ID validation
        if not re.match(r'^03$', field_id):
            return False, "Invalid Field ID in footer"

        # Total Counter validation
        if not re.match(r'^\d{6}$', total_counter):
            return False, "Total Counter format is not correct."
        if int(total_counter) != num_transactions:
            return False, f"Total Counter value does not match the number of transactions ({num_transactions})."

        # Control Sum validation
        if not re.match(r'^\d{12}$', control_sum):
            return False, "Control Sum format is not correct."
        if int(control_sum) != total_amount:
            return False, f"Control Sum value does not match the total amount of transactions ({total_amount})."

        return True, "Footer is valid"

    def run(self):
        with open(self.filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()

            num_transactions = len(lines) - 2
            amount_start = const.TRANSACTIONS_SLICES['Amount'][0]
            amount_end = const.TRANSACTIONS_SLICES['Amount'][1]
            total_amount = sum(int(line[amount_start:amount_end]) for line in lines if line.startswith('02'))

            results = [self._validate_header(line=lines[0]),
                       self._validate_transactions(lines=lines[1:-1]),
                       self._validate_footer(line=lines[-1],
                                             num_transactions=num_transactions,
                                             total_amount=total_amount)]

            if all(results[0]):
                return True, results
            return False, results
