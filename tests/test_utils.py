import unittest
from FixedFileIO import utils


class TestUtils(unittest.TestCase):
    def test_get_values_as_dict(self):
        """Tests that get_values_as_dict correctly
         extracts and returns values as a dictionary."""
        line = "01John              Smith               "
        slices = {'Field ID': (0, 2), 'Name': (2, 20), 'Surname': (20, 40)}
        expected = {'Field ID': '01', 'Name': 'John', 'Surname': 'Smith'}
        result = utils.get_values_as_dict(line, slices)
        self.assertEqual(result, expected)

    def test_format_record(self):
        """Tests that format_record correctly formats a dictionary
         into a string based on slice definitions."""
        record = {'Field ID': '01', 'Name': 'John', 'Surname': 'Smith'}
        slices = {'Field ID': (0, 2), 'Name': (2, 20), 'Surname': (20, 40)}
        expected_line = "01John              Smith               "
        result_line = utils.format_record(record, slices)
        self.assertEqual(result_line, expected_line)

    def test_check_fields_length_exceeds(self):
        """Tests that check_fields_length raises a ValueError"""
        with self.assertRaises(ValueError):
            utils.check_fields_length('Name', 'JohnJohnJohnJohnJohnJohnJohnJohnJohnJohn')

    def test_validate_field_value_invalid(self):
        """Tests that validate_field_value raises a ValueError for invalid values."""
        with self.assertRaises(ValueError):
            utils.validate_field_value('Amount', '40THOUSANDS')
        with self.assertRaises(ValueError):
            utils.validate_field_value('Name', 'John7')
