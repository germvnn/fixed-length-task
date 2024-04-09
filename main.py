import argparse
from FixedFileIO.handler import FixedWidthHandler
from FixedFileIO import constants as const


def read_values(handler: FixedWidthHandler):
    header, transactions, footer = handler.read_file()
    print(header)
    for transaction in transactions:
        transaction.pop('Reserved', None)
        print(transaction)
    footer.pop('Reserved', None)
    print(footer)


def add_transaction_cli(handler: FixedWidthHandler):
    while True:
        amount = input("Enter the transaction amount: ")
        try:
            amount = "{:.2f}".format(float(amount))
        except ValueError:
            print("Invalid amount. Please enter a numeric value.")
            continue

        currency = input("Enter the currency code: ").upper()
        if currency not in const.CURRENCIES:
            print(const.CURRENCY_ERROR)
            continue

        handler.add_transaction(amount=amount, currency=currency)
        break


def update_field_cli(handler: FixedWidthHandler):
    record_type = input("Enter record to update (header|transaction): ")
    field_name = input("Enter field name: ").title()
    field_value = input("Enter the new value: ")
    if field_name == "Currency" and field_value not in const.CURRENCIES:
        raise ValueError(const.CURRENCY_ERROR)
    counter = None
    if record_type == 'transaction':
        counter = input("Enter the transaction counter: ").zfill(6)
    try:
        handler.update_field(record_type=record_type,
                             field_name=field_name,
                             field_value=field_value if not field_name == "Currency" else field_value.upper(),
                             counter=counter)
    except KeyError:
        print(f"Field {field_name} does not exist in {record_type}.")
    except Exception as e:
        print(e)


def main():
    parser = argparse.ArgumentParser(description='CLI for Fixed File IO operations.')
    parser.add_argument('action', choices=['read', 'add', 'update'], help='Action to perform.')
    parser.add_argument('filepath', help='Path to the fixed-width file.')

    args = parser.parse_args()
    handler = FixedWidthHandler(filepath=args.filepath)

    match args.action:
        case 'read':
            read_values(handler)
        case 'add':
            add_transaction_cli(handler)
        case 'update':
            update_field_cli(handler)


if __name__ == '__main__':
    main()
