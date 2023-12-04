import json
import re  # Import regular expression module for email validation
import socket
import threading
from datetime import datetime, timedelta

from encrypt_decrypt import A3Encryption, A3Decryption

# Constants for file names
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
live_update_thread = None  # Thread for live updates
stop_flag = threading.Event()
encrypt = A3Encryption()
decrypt = A3Decryption()
logged_in_user = None  # Variable to store the currently logged-in user


def check_email_from_server(email: str):
    """
        Checking email in server if already has return true else false

        Returns:
            bool:
        """
    client.send(encrypt.start_encryption(f"check_email,{email}", "client").encode('utf-8'))
    data = client.recv(1024)
    if decrypt.startDecryption(data.decode('utf-8')) == "SUCCESS":
        return True
    else:
        return False


# Function for email validation
def is_valid_email(email, flag: bool):
    """
    Validate an email address using a basic regular expression.

    Parameters:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """

    email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
    patten = bool(re.match(email_pattern, email))
    check = check_email_from_server(email)
    (print("Invalid email format!") if not patten else print(
        "Email already exist!") if check else "") if flag else print(
        "Invalid email format!") if not patten else None if check else print("Email not found!")
    if not patten:
        return False
    if not check:
        if flag:
            return True
        else:
            return False
    return patten and not check


def handel_err(msg: str, data: str):
    if data == "":
        print(msg)
        return True
    else:
        return False


def register_user():
    """
        Register a new user by collecting information and saving it to the users file.

        Returns:
            None
        """
    print("---Register-----")
    username = input("Enter username: ")
    if handel_err("Invalid username", username):
        return
    email = input("Enter email address: ")
    # Validate email
    if not is_valid_email(email, True):
        return
    password = input("Enter password: ")
    if handel_err("Invalid password", password):
        return
    contact = input("Enter contact details: ")
    if handel_err("Invalid contact details", contact):
        return
    balance = int(input("Enter your balance: "))
    if handel_err("Invalid balance", str(balance)):
        return
    new_user = {"username": username, "email": email, "password": password, "contact": contact, "balance": balance}
    client.send(encrypt.start_encryption(f"add_user-{new_user}", "client").encode('utf-8'))
    data = client.recv(1024)
    if decrypt.startDecryption(data.decode('utf-8')) == "SUCCESS":
        print("Registration success.")
        return
    else:
        print("Registration fail.")
        return


def login_user():
    """
        Login function

        Returns:
            None
        """
    print("---Login section---")
    global logged_in_user
    email = input("Enter email address: ")
    # Validate email
    if not is_valid_email(email, False):
        return
    password = input("Enter password: ")
    if handel_err("Invalid password", password):
        return
    client.send(encrypt.start_encryption(f"login,{email},{password}", "client").encode('utf-8'))
    data = client.recv(1024)
    recv = decrypt.startDecryption(data.decode('utf-8'))
    logged_in_user = (print("Success") or json.loads(recv)) if recv != "FAIL" else (
            None or print("Login Fail.Wrong password!"))
    return logged_in_user


def bid(user):
    """
        Placing bids for login users by auction id

        Returns:
            None
        """
    print("---Making bids----")
    try:
        item_id = int(input("Enter id of you want to bid."))
        com = f"check_item,{item_id}"
        check: str = command(com)
        if check.startswith("Bidding"):
            print(check)
        elif check != "BAD":
            print(check)
            amount = input("Enter amount you want to bid!")
            try:
                bid_amount = float(amount)
            except ValueError:
                print("Invalid bid amount. Please enter a valid number.")
                return
            comm = f"bid,{user['id']},{item_id},{bid_amount}"
            status = command(comm)
            if status == "OK":
                print("Bid success.")
            else:
                print(status)

        else:
            print("Item not found!")
    except Exception as e:
        print(e)


def show_live():
    print("----Live auctions----")
    global stop_flag
    stop_flag = threading.Event()
    r = threading.Thread(target=receive_messages)
    r.start()
    start_live_update_thread()
    while live_update_thread:
        pass


def command(com: str):
    client.send(encrypt.start_encryption(com, "client").encode('utf-8'))
    data = client.recv(8192).decode("utf-8")
    result = decrypt.startDecryption(data)
    return result


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


def auction_list():
    """
        The auction list of all auction from server
        (input)1 for not ended auctions
        (input)2 for ended auctions

        Returns:
            None
        """
    print("----Auctions----")
    choice = input("1.Not ended auctions\n2.Ended auctions")
    "" if (choice == "1" or choice == "2") else (print("Invalid choice!") or auction_list())
    client.send(encrypt.start_encryption(f"auction_list,{choice}", "client").encode('utf-8'))
    data = client.recv(8192).decode("utf-8")
    auctions: dict = json.loads(decrypt.startDecryption(data))
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
                                                                                                      'highest_bidder'] is not None else ""
        print(f"=> Seller: {auction['seller']}       ")

        print()


def receive_messages():
    """
        Listening live update messages from server

        Returns:
            None
        """
    while not stop_flag.is_set():
        try:
            data = client.recv(1024)
            if not data:
                break
            decoded_data = decrypt.startDecryption(data.decode('utf-8'))
            print(decoded_data)

        except Exception as e:
            print(f"[ERROR] Error receiving message: {e}")
            break


def live_update():
    """
        Monitoring the live auctions status by auction id

        Returns:
            None
        """
    print("Enter the item id for live auction details (type 'exit' to stop):")
    global live_update_thread
    global logged_in_user
    items = None
    while True:
        item = input("")
        if item.lower() == 'exit':
            # Send a command to the server to stop live updates
            client.send(
                encrypt.start_encryption(f"stop_live_update,{items if items is not None else 1},{logged_in_user['id']}",
                                         "client").encode("utf-8"))
            live_update_thread = None
            stop_flag.set()
            break
        items = item
        send_command = encrypt.start_encryption(f"live_auction,{item},{logged_in_user['id']}", "client")
        client.send(send_command.encode("utf-8"))


def start_live_update_thread():
    """
        Start live update thread if not alive and none

        Returns:
            None
        """
    global live_update_thread
    if not live_update_thread or not live_update_thread.is_alive():
        live_update_thread = threading.Thread(target=live_update)
        live_update_thread.start()


def profile(logged_user: dict):
    """
        The show user account status

        Returns:
            None
        """
    user: dict = json.loads(command(f"login,{logged_user['email']},{logged_user['password']}"))
    print(f"|-----------User Information-----------|")
    print(f"> User name : {user['username']}")
    print(f"> Email     : {user['email']}")
    print(f"> Password  : {user['password']}")
    print(f"> Contact   : {user['contact']}")
    print(f"> Balance   : {user['balance']}")
    print("----------------end-----------------------")
    print("| 1.Edit user info | 2.Show won bids. |\n|3.Exit")
    while True:
        choice = input("Enter your choice (1-2) (type 3 to exit):")

        try:
            if choice == '1':
                edit_info(user)
            elif choice == '2':
                show_win(user)
            elif choice == '3':
                break
            else:
                print("Invalid choice!")
        except Exception as e:
            print(e)


def edit_info(user: dict):
    """
        To edit user information

        Returns:
            None
        """
    print("-----Edit user info--------")
    print(f"1.Edit username")
    print(f"2.Edit email")
    print(f"3.Edit contact address")
    print(f"4.Edit password")
    print(f"5.Add balance\n6.Exit")
    global logged_in_user
    while True:
        choice = input("Enter your choice (1-5)(type 6 to exit):")
        try:
            if choice == '1':
                new_name = input("Enter new username:")
                result = command(f"edit_info,{user['id']},username,{new_name}")
                logged_in_user = json.loads(result) if result != "FAIL" else (print("Error occurred!") or user)
            elif choice == '2':
                new_email = input("Enter new email:")
                result = command(f"edit_info,{user['id']},email,{new_email}")
                logged_in_user = json.loads(result) if result != "FAIL" else (print("Error occurred!") or user)
            elif choice == '3':
                new_contact = input("Enter new contact address:")
                result = command(f"edit_info,{user['id']},contact,{new_contact}")
                logged_in_user = json.loads(result) if result != "FAIL" else (print("Error occurred!") or user)
            elif choice == '4':
                new_password = input("Enter new password:")
                result = command(f"edit_info,{user['id']},password,{new_password}")
                logged_in_user = json.loads(result) if result != "FAIL" else (print("Error occurred!") or user)
            elif choice == '5':
                new_balance = int(input("Enter amount to add:"))
                result = command(f"edit_info,{user['id']},balance,{new_balance}")
                logged_in_user = json.loads(result) if result != "FAIL" else (print("Error occurred!") or user)
            elif choice == '6':
                break
            else:
                print("Invalid choice!")
        except Exception as e:
            print(e)


def show_win(user: dict):
    """
        To show the won bid item of user account

        Returns:
            None
        """
    print("------Won bids-----------")
    result = json.loads(command(f"won_bids,{user['id']}"))
    print("No won bids!") if len(result) == 0 else ""
    for item in result:
        print(f"Title       :{item['title']}")
        print(f"Description : {item['description']}")
        print(f"Image url   : {item['product_img']}")
        print(f"Last price  : {item['last_price']}")
        print("----------------------------------")


def create_auctions():
    """
        Create new auction item for  the auction system to create new item need to login first

        Returns:
            None
        """
    global logged_in_user
    print("-----Create auctions--------")
    title = input("Enter auction title: ")
    if handel_err("Invalid title", title):
        return
    description = input("Enter auction description: ")
    if handel_err("Invalid description", description):
        return
    img_url = input("Enter your product image url:")
    if handel_err("Invalid url", img_url):
        return
    base_price_str = int(input("Enter base price:"))
    try:
        base_price = int(base_price_str)
    except ValueError:
        print("Invalid base amount. Please enter a valid number.")
        return
    end_time_str = int(input("Enter date auction will end (1-24)hour: "))
    if 24 >= end_time_str >= 1:
        pass
    else:
        print("Enter day between 1-24!")
        return
    end_time = datetime.now() + timedelta(hours=end_time_str)
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M')
    result = command(
        f"create_auction,{title},{description},{img_url},{base_price},{end_time_str},{logged_in_user['username']}")
    print(f"Auction {result} created successfully.") if result != "FAIL" else print("Auction creation failed!")


def main_menu():
    """
    The main menu of the auction system.

    Returns:
        None
    """

    global logged_in_user

    while True:
        print("++++++Auction Management System+++++++++")
        print("| 1.Register User  | 2. Login         |")
        print("| 3.Create Auction | 4. Place Bids    |")
        print("| 5.Auction Status | 6. Live auctions |")
        print("| 7.Profile        | 8.Logout         |")
        print(f"|9.Exit           | Logged={True if logged_in_user else False}     |")

        choice = input("Enter your choice (1-8)(type 9 to exit): ")

        if choice == '1':
            register_user()
        elif choice == '2':
            logged_in_user = login_user()
        elif choice == '3':
            create_auctions()
        elif choice == '4':
            bid(logged_in_user) if logged_in_user else print("Please login before place an auction.")
        elif choice == '5':
            auction_list()
        elif choice == '6':
            show_live() if logged_in_user else print("Please login before to see live updates!")
        elif choice == '7':
            profile(logged_in_user) if logged_in_user else print("First you need to login!")
        elif choice == '8':
            logged_in_user = None
            print("Logout successful.")
        elif choice == '9':
            print("Exiting Auction Management System. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 8.")


if __name__ == '__main__':
    print("Starting client")
    host = "127.0.0.1"
    port = 5553
    client.connect((host, port))
    main_menu()
