# Auction Management System Documentation

## Overview

The Auction Management System is a simple command-line application that allows users to register, create auctions, place bids,live auction  and view auction status. The system uses JSON files to store user data, auction information, and bid records.To communicate between client and server using tcp protocol and encrypt decrypt methods.

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
### `filter_auctions(ended=False):`
Filter the ended auctions if true default false not filter
- **Parameters:**
- `ended` (boolean):Default False 
### `auction_status()`

Display the status of all auctions, including information such as title, description, end time, remaining time, highest bid, and seller.

### `main_menu()`

The main menu loop where users can choose various options like registering, logging in, creating auctions, placing bids, checking auction status, and logging out.

## Usage

1. Run the `aucion_server.py` script.
2. Run the `client.py` script.
3. Follow the on-screen instructions to interact with the system.
4. Choose options from the main menu to perform specific actions.
