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


def add_transaction_cli(handler):
    while True:
        amount = input("Enter the transaction amount: ")
        try:
            amount = "{:.2f}".format(float(amount))
        except ValueError:
            print("Invalid amount. Please enter a numeric value.")
            continue

        currency = input("Enter the currency code: ").upper()
        if currency not in const.CURRENCIES:
            print(f"Currency not recognized. Allowed currencies are: {', '.join(const.CURRENCIES)}")
            continue

        handler.add_transaction(amount=amount, currency=currency)
        break


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
            pass


if __name__ == '__main__':
    main()
