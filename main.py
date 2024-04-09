import argparse
from FixedFileIO.handler import FixedWidthHandler


def main():
    parser = argparse.ArgumentParser(description='CLI for Fixed File IO operations.')
    parser.add_argument('action', choices=['read', 'write', 'update'], help='Action to perform.')
    parser.add_argument('filepath', help='Path to the fixed-width file.')

    args = parser.parse_args()

    handler = FixedWidthHandler(filepath=args.filepath)

    match args.action:
        case 'read':
            pass
        case 'write':
            pass
        case 'update':
            pass


if __name__ == '__main__':
    main()
