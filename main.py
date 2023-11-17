import os
import json
from datetime import datetime, timedelta
import re  # Import regular expression module for email validation

# Constants for file names
USERS_FILE = 'users.txt'
AUCTIONS_FILE = 'auctions.txt'
BIDS_FILE = 'bids.txt'


# Function to load data from a file
def load_data(file_name):
    """
    Load data from a JSON file.

    Parameters:
        file_name (str): The name of the file to load.

    Returns:
        list: The loaded data as a list.
    """
    data = []
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            data = json.load(file)
    return data


# Function to save data to a file
def save_data(file_name, data):
    """
    Save data to a JSON file.

    Parameters:
        file_name (str): The name of the file to save to.
        data (list): The data to be saved.

    Returns:
        None
    """
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=2)


# Function for email validation
def is_valid_email(email):
    """
    Validate an email address using a basic regular expression.

    Parameters:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return bool(re.match(email_pattern, email))


# Function for user registration
def register_user():
    """
    Register a new user by collecting information and saving it to the users file.

    Returns:
        None
    """
    username = input("Enter username: ")
    password = input("Enter password: ")
    contact = input("Enter contact details: ")
    email = input("Enter email address: ")

    # Validate email
    if not is_valid_email(email):
        print("Invalid email address.")
        return

    users = load_data(USERS_FILE)
    users.append({'username': username, 'password': password, 'contact': contact, 'email': email})
    save_data(USERS_FILE, users)
    print("User registered successfully!")


# Function for user login
def login_user():
    """
    Log in a user by checking their credentials against the stored data.

    Returns:
        str or None: The username if login is successful, None otherwise.
    """
    username = input("Enter username: ")
    password = input("Enter password: ")

    users = load_data(USERS_FILE)

    for user in users:
        if user['username'] == username and user['password'] == password:
            print("Login successful!")
            return username  # Return the username upon successful login

    print("Invalid username or password.")
    return None


# Function for calculation time
def cal_time_remain(time_remaining):
    """
    Calculate the time remaining in days, hours, minutes, and seconds.

    Parameters:
        time_remaining (timedelta): The time remaining.

    Returns:
        str: The formatted time remaining.
    """
    days, seconds = divmod(time_remaining.total_seconds(), 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{int(days)}d {int(hours)}h {int(minutes)}min {int(seconds)}s"


# Function for creating an auction
def create_auction(username):
    """
    Create a new auction by collecting information and saving it to the auctions file.

    Parameters:
        username (str): The username of the seller.

    Returns:
        None
    """
    title = input("Enter auction title: ")
    description = input("Enter auction description: ")
    end_time_str = input("Enter auction end time (YYYY-MM-DD HH:MM): ")
    end_time_str = end_time_str.replace('24:00', '00:00')

    # Validate date format
    try:
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M')
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD HH:MM.")
        return

    auctions = load_data(AUCTIONS_FILE)
    auction_id = len(auctions) + 1
    auctions.append({
        'id': auction_id,
        'title': title,
        'description': description,
        'end_time': end_time_str,
        'highest_bidder': None,
        'highest_bid': 0,
        'seller': username  # Add seller information
    })
    save_data(AUCTIONS_FILE, auctions)
    print(f"Auction {auction_id} created successfully!")


# Function for placing a bid
def place_bid(username):
    """
    Place a bid on an existing auction.

    Parameters:
        username (str): The username of the bidder.

    Returns:
        None
    """
    auction_id = int(input("Enter auction ID to bid on: "))

    auctions = load_data(AUCTIONS_FILE)
    bids = load_data(BIDS_FILE)

    if auction_id <= 0 or auction_id > len(auctions):
        print("Invalid auction ID.")
        return

    auction = auctions[auction_id - 1]
    end_time = datetime.strptime(auction['end_time'], '%Y-%m-%d %H:%M')
    time_remaining = end_time - datetime.now()
    if time_remaining <= timedelta(seconds=0):
        print(f"Bidding for this auction has ended.\nThis item is Sold to {auction['highest_bidder']}.")
        return
    print(f"Time Remaining: {cal_time_remain(time_remaining)}")
    print(f"Highest Bid: {auction['highest_bid']} by {auction['highest_bidder']}")

    bid_amount_str = input("Enter bid amount: ")

    # Validate bid amount
    try:
        bid_amount = float(bid_amount_str)
    except ValueError:
        print("Invalid bid amount. Please enter a valid number.")
        return

    if bid_amount < auction['highest_bid']:
        accepted_amount = auction['highest_bid'] + 1
        print(f"You need to bid at least {accepted_amount} to become the highest bidder.")
        return

    auctions[auction_id - 1]['highest_bid'] = bid_amount
    auctions[auction_id - 1]['highest_bidder'] = username

    bids.append({
        'auction_id': auction_id,
        'bidder': auctions[auction_id - 1]['highest_bidder'],
        'bid_amount': bid_amount
    })

    save_data(AUCTIONS_FILE, auctions)
    save_data(BIDS_FILE, bids)

    print("Bid placed successfully!")


# Function to display auction status
def auction_status():
    """
    Display the status of all auctions.

    Returns:
        None
    """
    auctions = load_data(AUCTIONS_FILE)

    for auction in auctions:
        end_time = datetime.strptime(auction['end_time'], '%Y-%m-%d %H:%M')
        time_remaining = end_time - datetime.now()

        print(f"---Auction ID: {auction['id']}----")
        print(f"=> Title: {auction['title']}         ")
        print(f"=> Description: {auction['description']} ")
        print(f"=> End Time: {auction['end_time']} ")

        if time_remaining <= timedelta(seconds=0):
            print(f"=> Sold to: {auction['highest_bidder']} with bid {auction['highest_bid']} ")
        else:
            print(f"=> Time Remaining: {cal_time_remain(time_remaining)} |")
            print(f"=> Highest Bid: {auction['highest_bid']} by {auction['highest_bidder']} ")
        print(f"=> Seller: {auction['seller']}       ")

        # Add an empty line between auctions for better readability
        print()


# Main menu
def main_menu():
    """
    The main menu of the auction system.

    Returns:
        None
    """
    logged_in_user = None  # Variable to store the currently logged-in user

    while True:
        print("++++Auction Management System++++++")
        print("| 1.Register User  | 2. Login      |")
        print("| 3.Create Auction | 4. Place Bid  |")
        print("| 5.Auction Status | 6. Logout     |")
        print(f"| 7.Exit           | Logged={True if logged_in_user else False}  |")

        choice = input("Enter your choice (1-7): ")

        if choice == '1':
            register_user()
        elif choice == '2':
            logged_in_user = login_user()
        elif choice == '3':
            if logged_in_user:
                create_auction(logged_in_user)
            else:
                print("Please log in before creating an auction.")
        elif choice == '4':
            if logged_in_user:
                place_bid(logged_in_user)
            else:
                print("Please log in before placing a bid.")
        elif choice == '5':
            auction_status()
        elif choice == '6':
            logged_in_user = None
            print("Logout successful.")
        elif choice == '7':
            print("Exiting Auction Management System. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")


if __name__ == "__main__":
    # Create empty files if they don't exist
    for file_name in [USERS_FILE, AUCTIONS_FILE, BIDS_FILE]:
        if not os.path.exists(file_name):
            with open(file_name, 'w') as file:
                json.dump([], file)

    main_menu()
