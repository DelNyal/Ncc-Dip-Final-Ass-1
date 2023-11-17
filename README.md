# Auction Management System Documentation

## Overview

The Auction Management System is a simple command-line application that allows users to register, create auctions, place bids, and view auction status. The system uses JSON files to store user data, auction information, and bid records.

## Files

- `main.py`: The main Python script containing the auction system code.
- `users.txt`: JSON file storing user data.
- `auctions.txt`: JSON file storing auction information.
- `bids.txt`: JSON file storing bid records.

## Functions

### `load_data(file_name)`

Load data from a JSON file.

- **Parameters:**
  - `file_name` (str): The name of the file to load.

- **Returns:**
  - `list`: The loaded data.

### `save_data(file_name, data)`

Save data to a JSON file.

- **Parameters:**
  - `file_name` (str): The name of the file to save.
  - `data` (list): The data to save.

### `is_valid_email(email)`

Validate an email address using a regular expression.

- **Parameters:**
  - `email` (str): The email address to validate.

- **Returns:**
  - `bool`: True if the email is valid, False otherwise.

### `register_user()`

Register a new user by collecting user information and validating the email.

### `login_user()`

Log in a user by checking the entered username and password against existing user data.

- **Returns:**
  - `str`: The username upon successful login, None otherwise.

### `cal_time_remain(time_remaining)`

Calculate the remaining time in days, hours, minutes, and seconds.

- **Parameters:**
  - `time_remaining` (timedelta): The remaining time as a timedelta object.

- **Returns:**
  - `str`: A formatted string representing the remaining time.

### `create_auction(username)`

Create a new auction by collecting auction information and validating the end time format.

- **Parameters:**
  - `username` (str): The username of the seller.

### `place_bid(username)`

Place a bid on a specific auction by collecting bid information and updating auction data.

- **Parameters:**
  - `username` (str): The username of the bidder.

### `auction_status()`

Display the status of all auctions, including information such as title, description, end time, remaining time, highest bid, and seller.

### `main_menu()`

The main menu loop where users can choose various options like registering, logging in, creating auctions, placing bids, checking auction status, and logging out.

## Usage

1. Run the `main.py` script.
2. Follow the on-screen instructions to interact with the system.
3. Choose options from the main menu to perform specific actions.

## Testing

Testing can be performed using unit tests for individual functions. Consider testing different scenarios, including valid and invalid inputs, to ensure the robustness of the system.

Example Test:
```python
# import necessary modules
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

