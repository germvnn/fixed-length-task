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
                    transaction.pop('Reserved', None)
                    transactions.append(transaction)
                elif field_id == self.field_id_footer:  # Footer
                    footer = utils.get_values_as_dict(line, const.FOOTER_SLICES)
                    footer.pop('Reserved', None)
        return header, transactions, footer

    def add_transaction(self, amount, currency):
        slices = const.TRANSACTIONS_SLICES

        amount_start = slices['Amount'][0]
        amount_end = slices['Amount'][1]

        reserved_start = slices['Reserved'][0]
        reserved_end = slices['Amount'][1]

        with open(self.filepath, 'r+', encoding='utf-8') as file:
            lines = file.readlines()

            # Number of inserted transaction
            next_counter = str(len(lines) - 1).zfill(6)
            amount_formatted = f"{int(float(amount) * 100):0{amount_end -amount_start}d}"

            transaction_line = (
                self.field_id_transaction +
                next_counter +
                amount_formatted +
                currency +
                ' '.ljust(reserved_end - reserved_start)
            )

            control_sum = sum(int(line[amount_start:amount_end])
                              for line in lines if line.startswith(self.field_id_transaction)) + int(amount_formatted)
            control_sum_formatted = f"{control_sum:0{amount_end-amount_start}d}"

            lines.insert(-1, transaction_line + '\n')

            # Update footer
            updated_footer = (f"{self.field_id_footer}"
                              f"{next_counter}"
                              f"{control_sum_formatted}"
                              f"{' ' * (reserved_end - reserved_start)}")
            lines[-1] = updated_footer

            file.seek(0)
            file.writelines(lines)
            file.truncate()

    def update_field(self, record_type, field_name, value):
        pass
