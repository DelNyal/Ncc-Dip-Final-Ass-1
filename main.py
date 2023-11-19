import os
import json
from datetime import datetime, timedelta
import re  # Import regular expression module for email validation

# Constants for file names
USERS_FILE = 'users.txt'
AUCTIONS_FILE = 'auctions.txt'
BIDS_FILE = 'bids.txt'
logged_in_user = None  # Variable to store the currently logged-in user


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
    users = load_data(USERS_FILE)
    email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
    patten = bool(re.match(email_pattern, email))
    check = next((user for user in users if user['email'] == email), False)
    print("Invalid email format!") if not patten else print("Email already exist!") if check else ""
    return patten and not check


# Function for user registration
def register_user():
    """
    Register a new user by collecting information and saving it to the users file.

    Returns:
        None
    """
    print("---Register-----")
    username = input("Enter username: ")
    (print("Invalid username") or main_menu()) if username == "" else None
    password = input("Enter password: ")
    (print("Invalid password") or main_menu()) if password == "" else None
    contact = input("Enter contact details: ")
    (print("Invalid contact details") or main_menu()) if contact == "" else None
    email = input("Enter email address: ")
    # Validate email
    if not is_valid_email(email): main_menu()
    users = load_data(USERS_FILE)
    users.append({'username': username, 'password': password, 'contact': contact, 'email': email})
    save_data(USERS_FILE, users)
    print("User registered successfully!")


# Function for user login
def login_user():
    """
    Log in a user by checking their credentials against the stored data.

    Returns:
        str or None: The email if login is successful, None otherwise.
    """
    print("---Login----")
    users = load_data(USERS_FILE)
    email = input("Enter email: ")
    None if next((user for user in users if user['email'] == email), False) else (
            print("Email is not registered!") or main_menu())
    password = input("Enter password: ")
    for user in users:
        if user['email'] == email and user['password'] == password:
            print("Login successful!")
            return user['username']  # Return the username upon successful login

    print("Wrong password.")
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
    base_price_str = int(input("Enter base price:"))
    try:
        base_price = float(base_price_str)
    except ValueError:
        print("Invalid base amount. Please enter a valid number.")
        return
    end_time_str = int(input("Enter date auction will end (1-7)day: "))
    if 7 >= end_time_str >= 1:
        pass
    else:
        print("Enter day between 1-7!")
        return
    end_time = datetime.now() + timedelta(days=end_time_str)
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M')
    auctions = load_data(AUCTIONS_FILE)
    auction_id = len(auctions) + 1
    auctions.append({
        'id': auction_id,
        'title': title,
        'description': description,
        "base_price": base_price,
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
    print(f"Title:{auction['title']}")
    if time_remaining <= timedelta(seconds=0):
        print(f"Bidding for this auction has ended.\nThis item is Sold to {auction['highest_bidder']}.")
        return
    print(f"Time Remaining: {cal_time_remain(time_remaining)}")
    print(f"Highest Bid: {auction['highest_bid']} by {auction['highest_bidder']}") if auction[
                                                                                          'highest_bidder'] is not None else print(
        f"Base price: {auction['base_price']} by {auction['seller']}")

    bid_amount_str = input("Enter bid amount: ")
    highest_bid = auction['highest_bid'] if auction['highest_bidder'] is not None else auction['base_price']

    # Validate bid amount
    try:
        bid_amount = float(bid_amount_str)
    except ValueError:
        print("Invalid bid amount. Please enter a valid number.")
        return

    if bid_amount <= highest_bid:
        accepted_amount = highest_bid + 1
        print(f"You need to bid at least {accepted_amount} to become the highest bidder.")
        return

    auctions[auction_id - 1]['highest_bid'] = bid_amount
    auctions[auction_id - 1]['highest_bidder'] = username

    bids.append({
        'auction_id': auction_id,
        'bidder': auctions[auction_id - 1]['highest_bidder'],
        'bid_amount': bid_amount,
        'modify_date': datetime.now().strftime('%Y-%m-%d %H:%M')
    })

    save_data(AUCTIONS_FILE, auctions)
    save_data(BIDS_FILE, bids)

    print("Bid placed successfully!")


# Function to filter the ended auctions
def filter_auctions(ended=False):
    """
    Fileter the auctions base the end status
    Parameters:
        ended (boolean) :True to filer ended auction,Default  not filtered
    Returns:
        List : the filtered auctions
    """
    auctions = load_data(AUCTIONS_FILE)
    filtered_auctions = []
    for auction in auctions:
        end_time = datetime.strptime(auction['end_time'], '%Y-%m-%d %H:%M')
        time_remaining = end_time - datetime.now()
        filtered_auctions.append(auction) if ended and time_remaining.total_seconds() > 0 else filtered_auctions.append(auction) if not ended else ""
    return filtered_auctions


# Function to display auction status
def auction_status():
    """
    Display the status of all auctions.

    Returns:
        None
    """
    show_end = input("Press (y) to see only open auctions:")
    auctions = filter_auctions(True) if show_end == "y" else filter_auctions(False)
    for auction in auctions:
        end_time = datetime.strptime(auction['end_time'], '%Y-%m-%d %H:%M')
        time_remaining = end_time - datetime.now()
        ended = "Ended" if time_remaining <= timedelta(seconds=0) else "Open"
        print(f"---Auction ID: {auction['id']}| Status={ended}----")
        print(f"=> Title: {auction['title']}         ")
        print(f"=> Description: {auction['description']} ")
        print(f"=> Base price:{auction['base_price']}")
        print(f"=> End Time: {auction['end_time']} ")

        if time_remaining <= timedelta(seconds=0):
            print(f"=> Sold to: {auction['highest_bidder']} with bid {auction['highest_bid']} ")
        else:
            print(f"=> Time Remaining: {cal_time_remain(time_remaining)} |")
            print(f"=> Highest Bid: {auction['highest_bid']} by {auction['highest_bidder']} ") if auction[
                                                                                                      'highest_bidder'] is None else ""
        print(f"=> Seller: {auction['seller']}       ")

        print()


# Main menu
def main_menu():
    """
    The main menu of the auction system.

    Returns:
        None
    """

    global logged_in_user

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
