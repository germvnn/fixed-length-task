import unittest
from unittest.mock import patch
from FixedFileIO.handler import FixedWidthHandler


class TestFixedWidthHandler(unittest.TestCase):

    def setUp(self):
        """Test configuration."""
        self.filepath = 'testfile.fwf'
        self.handler = FixedWidthHandler(self.filepath)

    @patch('FixedFileIO.handler.open',
           unittest.mock.mock_open(read_data="01Name    \n02Transact\n03Footer  "), create=True)
    @patch('FixedFileIO.handler.logger')
    def test_read_file_success(self, mock_logger):
        """Ensures that the `read_file` method correctly parses a fixed-width file"""
        header, transactions, footer = self.handler.read_file()
        self.assertIsNotNone(header)
        self.assertEqual(len(transactions), 1)
        self.assertIsNotNone(footer)
        mock_logger.info.assert_called_with("File successfully loaded")

    @patch('FixedFileIO.handler.open', unittest.mock.mock_open(), create=True)
    @patch('FixedFileIO.handler.logger')
    def test_write_file_success(self, mock_logger):
        """Verifies that the `write_file` method correctly formats data"""
        header = {'Field ID': '01', 'Name': 'Name'}
        transactions = [{'Field ID': '02', 'Amount': '100', 'Currency': 'USD'}]
        footer = {'Field ID': '03', 'Total Counter': '1', 'Control sum': '100'}
        self.handler.write_file(header, transactions, footer)
        mock_logger.info.assert_called_with("File successfully wrote")

    @patch('FixedFileIO.handler.FixedWidthHandler.write_file')
    @patch('FixedFileIO.handler.FixedWidthHandler.read_file')
    def test_add_transaction_success(self, mock_read_file, mock_write_file):
        """Tests that the `add_transaction` method successfully adds a new transaction"""
        mock_read_file.return_value = ({}, [], {})
        self.handler.add_transaction('100', 'USD')
        mock_write_file.assert_called()

    @patch('FixedFileIO.handler.FixedWidthHandler.write_file')
    @patch('FixedFileIO.handler.FixedWidthHandler.read_file')
    def test_update_field_success(self, mock_read_file, mock_write_file):
        """Confirms that the `update_field` method can correctly update values"""
        mock_read_file.return_value = ({'Field ID': '01', 'Name': 'OldName'}, [], {})
        self.handler.update_field('header', 'Name', 'NewName', None)
        mock_write_file.assert_called()
