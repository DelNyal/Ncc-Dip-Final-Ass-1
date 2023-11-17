import unittest
from datetime import datetime, timedelta

# import functions to test
from main import load_data,main_menu, is_valid_email, cal_time_remain


class TestAuctionSystem(unittest.TestCase):

    def test_load_and_save_data(self):
        # Write test cases for load_data and save_data functions
        load_data("bids")

    def test_is_valid_email(self):
        # Write test cases for is_valid_email function
        is_valid_email("a@gmail.com")

    def test_main(self):
        main_menu()



# Run the tests
if __name__ == '__main__':
    unittest.main()
