from . import constants as const
from . import utils


class FixedWidthHandler:

    field_id_header = '01'
    field_id_transaction = '02'
    field_id_footer = '03'

    def __init__(self, filepath):
        self.filepath = filepath

    def read_file(self):
        header, transactions, footer = None, [], None
        with open(self.filepath, 'r', encoding='utf-8') as file:
            for line in file:
                field_id = line[0:2]
                if field_id == self.field_id_header:  # Header
                    header = utils.get_values_as_dict(line, const.HEADER_SLICES)
                elif field_id == self.field_id_transaction:  # Transaction
                    transaction = utils.get_values_as_dict(line, const.TRANSACTIONS_SLICES)
                    transactions.append(transaction)
                elif field_id == self.field_id_footer:  # Footer
                    footer = utils.get_values_as_dict(line, const.FOOTER_SLICES)
        return header, transactions, footer

    def write_file(self, header, transactions, footer):
        with open(self.filepath, 'w', encoding='utf-8') as file:
            # Header
            header_line = self.format_record(header, const.HEADER_SLICES)
            file.write(header_line + '\n')

            # Transactions
            for transaction in transactions:
                transaction_line = self.format_record(transaction, const.TRANSACTIONS_SLICES)
                file.write(transaction_line + '\n')

            # Footer
            footer['Control sum'] = sum(int(transaction['Amount']) for transaction in transactions)
            footer_line = self.format_record(footer, const.FOOTER_SLICES)
            file.write(footer_line + '\n')

    def format_record(self, record, slices):
        line = ''
        for field, (start, end) in slices.items():
            value = str(record.get(field, ''))
            length = end - start

            if field in ['Counter', 'Amount', 'Control sum']:
                value = value.zfill(length)
                line += value.rjust(length)
            else:
                line += value.ljust(length)
        return line

    def _generate_transaction_line(self, counter, amount, currency):
        amount_formatted = f"{amount:012d}"
        reserved_space = ' ' * (120 - 23)
        return f"{self.field_id_transaction}{counter}{amount_formatted}{currency}{reserved_space}"

    def _calculate_control_sum(self, lines, amount=0):
        return sum(int(line[8:20]) for line in lines if line.startswith(self.field_id_transaction)) + amount

    def _update_footer(self, lines, counter, amount=0):
        control_sum = self._calculate_control_sum(lines=lines, amount=amount)
        control_sum_formatted = f"{control_sum:012d}"
        lines[-1] = f"{self.field_id_footer}{counter}{control_sum_formatted}{' ' * (120 - 23)}"

    def add_transaction(self, amount, currency):

        with open(self.filepath, 'r+', encoding='utf-8') as file:
            lines = file.readlines()

            # Counter of inserted transaction
            next_counter = str(len(lines) - 1).zfill(6)  # -2 (header, footer) +1 (new_transaction)
            new_amount = int(float(amount) * 100)

            transaction_line = self._generate_transaction_line(counter=next_counter,
                                                               amount=new_amount,
                                                               currency=currency)

            # Insert transaction line
            lines.insert(-1, transaction_line + '\n')

            # Update footer
            self._update_footer(lines=lines, counter=next_counter, amount=new_amount)

            # Write file
            file.seek(0)
            file.writelines(lines)
            file.truncate()

    def _update_header_field(self, header, field_name, value):
        if field_name not in const.HEADER_FIELDS:
            raise ValueError(f"{field_name} is not a valid field for header.")
        header[field_name] = value

    def _update_transaction_field(self, transactions, field_name, value, counter):
        if field_name not in const.TRANSACTION_FIELDS:
            raise ValueError(f"{field_name} is not a valid field for transaction.")
        for transaction in transactions:
            if transaction['Counter'] == counter:
                transaction[field_name] = value
                return
        raise ValueError(f"No transaction with counter {counter} found.")

    def update_field(self, record_type, field_name, field_value, counter=None):
        header, transactions, footer = self.read_file()

        try:
            value = const.FIELD_TYPES[field_name](field_value)
        except ValueError:
            print(f"Cannot convert {field_value} to {const.FIELD_TYPES[field_name]}.")
            return

        try:
            match record_type:
                case 'header':
                    self._update_header_field(header=header, field_name=field_name, value=value)
                case 'transaction':
                    if counter is None:
                        raise ValueError("Counter is required for updating a transaction.")
                    self._update_transaction_field(transactions=transactions,
                                                   field_name=field_name,
                                                   value=value,
                                                   counter=counter)
                case 'footer':
                    print("Footer is being updated automatically.")
                case _:
                    raise ValueError(f"Unknown record type: {record_type}")
            self.write_file(header=header, transactions=transactions, footer=footer)
        except ValueError as e:
            print(e)
