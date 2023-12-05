import json
import os
import socket
import threading
import time
from datetime import datetime, timedelta

from server import Server

# Constants for file names
USERS_FILE = 'users.txt'
AUCTIONS_FILE = 'auctions.txt'
BIDS_FILE = 'bids.txt'


def init_db():
    # Create empty files if they don't exist
    for file_name in [USERS_FILE, AUCTIONS_FILE, BIDS_FILE]:
        if not os.path.exists(file_name):
            with open(file_name, 'w') as file:
                json.dump([], file)


class ClientModel:
    """
        Creating clilentmodel to handle many clients

        Returns:
            None
        """
    def __init__(self, client: Server, item_id: int, user_id: int):
        self.client = client
        self.item_id = item_id
        self.user_id = user_id

    def user_id(self):
        return self.user_id

    def client(self):
        return self.client

    def item_id(self):
        return self.item_id


class AuctionServer:
    def __init__(self):
        self.clients = []
        self.live_update_clients = set()  # Clients requesting live updates
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('127.0.0.1', 5553))
        self.server.settimeout(5)
        self.server.listen(5)
        self.update_item = None
        self.sent_winner = None

    def broadcast(self, message):
        for client in self.clients:
            try:
                client.send(message)
            except Exception as e:
                print(f"[ERROR] Failed to send message to a client: {e}")
                self.clients.remove(client)
                self.live_update_clients.discard(client)

    def handle_client(self, client_socket):
        client_server = Server(client_socket)
        self.clients.append(client_server)

        while True:
            try:
                data = client_server.recv()
                print(data)
                if not data:
                    break
                self.handle_command(client_server, data)

            except Exception as e:
                print(f"[ERROR] Error handling client: {e}")
                break

        self.clients.remove(client_server)
        self.live_update_clients.discard(client_server)
        client_socket.close()

    def edit_info(self, user_id, key, value):
        try:
            users = self.load_data(USERS_FILE)
            users[int(user_id) - 1][key] = value if key != "balance" else users[int(user_id) - 1][key] + int(value)
            self.save_data(USERS_FILE, users)
            return users[int(user_id) - 1]
        except Exception as e:
            print(e)
            return None

    def show_won(self, user_id: int):
        auctions = self.load_data(AUCTIONS_FILE)
        items = []
        for auction in auctions:
            end_time = datetime.strptime(auction['end_time'], '%Y-%m-%d %H:%M')
            time_remaining = end_time - datetime.now()
            if time_remaining <= timedelta(seconds=0):
                if user_id == auction['highest_bidder_id']:
                    item = {"id": auction['id'], "title": auction['title'], "description": auction['description'],
                            "product_img": auction['product_img'], "last_price": auction['highest_bid']}
                    items.append(item)
        return items

    def create_auctions(self, title: str, description: str, img_url: str, base_price: int, end_time_str: str,
                        seller: str):
        try:
            auctions = self.load_data(AUCTIONS_FILE)
            auction_id = len(auctions) + 1
            new_auction = {
                'id': auction_id,
                'title': title,
                'description': description,
                'product_img': img_url,
                "base_price": base_price,
                'end_time': end_time_str,
                'highest_bidder': None,
                'highest_bidder_id': None,
                'highest_bid': 0,
                'seller': seller
            }
            auctions.append(new_auction)
            self.save_data(AUCTIONS_FILE, auctions)
            return auction_id
        except Exception as e:
            print(e)
            return "FAIL"

    def handle_command(self, client_socket: Server, command: str):
        if command.startswith('login'):
            _, email, password = command.split(',')
            user = self.check_email(email)
            client_socket.send(json.dumps(user)) if user["password"] == password else client_socket.send("FAIL")
        elif command.startswith("create_auction"):
            _, title, description, img_url, base_price, end_time, username = command.split(',')
            result = self.create_auctions(title, description, img_url, int(base_price), end_time, username)
            client_socket.send(str(result)) if result != "FAIL" else client_socket.send("FAIL")
        elif command.startswith("won_bids"):
            _, user_id = command.split(',')
            result = self.show_won(int(user_id))
            client_socket.send(json.dumps(result))
        elif command.startswith("edit_info"):
            _, user_id, key, value = command.split(',')
            result = self.edit_info(user_id, key, value)
            client_socket.send(json.dumps(result)) if result else client_socket.send("FAIL")

        elif command.startswith("check_item"):
            auction_id = int(command.split(',')[1])
            self.check_item(client_socket, auction_id)

        elif command.startswith('bid'):
            _, user_id, item, bid_amount = command.split(',')
            bid_amount = float(bid_amount)
            self.make_bid(client_socket, int(item), bid_amount, int(user_id))
        elif command.startswith('auction_list'):
            ended = True if command.split(',')[1] == "1" else False
            response = json.dumps(self.filter_auctions(ended))
            client_socket.send(response)

        elif command.startswith('live_auction'):
            try:
                _, item, user_id = command.split(',')
                self.handle_live(client_socket, int(item), int(user_id))
            except Exception as e:
                print(e)
                client_socket.send("Invalid input!")

        elif command.startswith('notify_live_update'):
            # Notify the client that live auction updates are available
            client_socket.send("Enter '5' for live auction updates.")

            # Add the client to the set of clients requesting live updates
            self.live_update_clients.add(client_socket)

        elif command.startswith('stop_live_update'):
            # Acknowledge the client's request to stop live updates
            _, item_id, user_id = command.split(',')
            try:
                client_socket.send('STOP_LIVE_UPDATE\n')
                # Remove the client from the set of clients requesting live updates
                self.live_update_clients.discard(ClientModel(client_socket, int(item_id), int(user_id)))
            except Exception as e:
                print(e)
        elif command.startswith("login"):
            email = command.split(',')[1]
            password = command.split(',')[2]
            user = self.check_email(email)
            client_socket.send(user) if user["password"] == password else client_socket.send("FAIL")

        elif command.startswith('check_email'):
            email = command.split(',')[1]
            client_socket.send("SUCCESS") if self.check_email(email) else client_socket.send("FAIL")
        elif command.startswith('add_user'):
            data = command.split('-')[1]
            print(data)
            client_socket.send("SUCCESS") if self.add_user(data) else client_socket.send("FAIL")
        else:
            client_socket.send('INVALID_COMMAND')

    def make_bid(self, client: Server, auction_id: int, bid_amount: float, user_id: int):
        auctions = self.load_data(AUCTIONS_FILE)
        users = self.load_data(USERS_FILE)
        bids = self.load_data(BIDS_FILE)

        print(auctions)
        auction = auctions[auction_id - 1]
        print(auction)
        highest_bid = auction['highest_bid'] if auction['highest_bidder'] is not None else auction['base_price']
        print(highest_bid)
        if bid_amount > users[user_id - 1]["balance"]:
            client.send(f"Not enough balance to make bid.\nRemain Balance={users[user_id - 1]['balance']}")
            return
        elif bid_amount <= highest_bid:
            accepted_amount = highest_bid + 1
            client.send(f"You need to bid at least {accepted_amount} to become the highest bidder.")
            return

        auctions[auction_id - 1]['highest_bid'] = bid_amount
        auctions[auction_id - 1]['highest_bidder'] = users[user_id - 1]["username"]
        auctions[auction_id - 1]['highest_bidder_id'] = users[user_id - 1]["id"]
        bids.append({
            'auction_id': auction_id,
            'bidder': auctions[auction_id - 1]['highest_bidder'],
            'bid_amount': bid_amount,
            'modify_date': datetime.now().strftime('%Y-%m-%d %H:%M')
        })

        self.save_data(AUCTIONS_FILE, auctions)
        self.save_data(BIDS_FILE, bids)
        end_time = datetime.strptime(auction['end_time'], '%Y-%m-%d %H:%M')
        time_remaining = end_time - datetime.now()
        data = f"Time Remaining: {self.cal_time_remain(time_remaining)}\n"
        print(f"Time Remaining: {self.cal_time_remain(time_remaining)}")
        data += f"Highest Bid: {auction['highest_bid']} by {auction['highest_bidder']}" if auction[
                                                                                               'highest_bidder'] is not None else f"Base price: {auction['base_price']} by {auction['seller']}"
        self.update_item = {"item_id": auction_id, "user_id": user_id, "msg": data, "from": "bid"}
        client.send("OK")

    def check_item(self, client: Server, auction_id: int):
        auctions = self.load_data(AUCTIONS_FILE)
        if auction_id <= 0 or auction_id > len(auctions):
            print("Invalid auction ID.")
            client.send("BAD")
        else:
            auction = auctions[auction_id - 1]
            end_time = datetime.strptime(auction['end_time'], '%Y-%m-%d %H:%M')
            time_remaining = end_time - datetime.now()
            print(f"Title:{auction['title']}")
            if time_remaining <= timedelta(seconds=0):
                print(f"Bidding for this auction has ended.\nThis item is Sold to {auction['highest_bidder']}.")
                client.send(f"Bidding for this auction has ended.\nThis item is Sold to {auction['highest_bidder']}.")
                return
            data = f"Time Remaining: {self.cal_time_remain(time_remaining)}\n"
            print(f"Time Remaining: {self.cal_time_remain(time_remaining)}")
            data += f"Highest Bid: {auction['highest_bid']} by {auction['highest_bidder']}" if auction[
                                                                                                   'highest_bidder'] is not None else f"Base price: {auction['base_price']} by {auction['seller']}"
            client.send(data)

    def broadcast_thread(self, message):

        copy_set = self.live_update_clients.copy()
        for client in copy_set:
            try:

                if message["from"] == "live":
                    if client.user_id == message['user_id']:
                        client.client.send(message['msg'])
                else:
                    if client.item_id == message['item_id']:
                        client.client.send(message["msg"])

            except Exception as e:
                print(f"[ERROR] Failed to send message to a client: {e}")
                self.clients.remove(client.client)
                self.live_update_clients.discard(client)

    def send_winner_thread(self):
        copy_set = self.live_update_clients.copy()
        for client in copy_set:
            try:
                self.sent_to_winner(client)

            except Exception as e:
                print(e)

    def sent_to_winner(self, client: ClientModel):
        time.sleep(1)
        auctions = self.load_data(AUCTIONS_FILE)
        users = self.load_data(USERS_FILE)
        auction = auctions[client.item_id - 1]
        user = users[client.user_id - 1]
        end_time = datetime.strptime(auction['end_time'], '%Y-%m-%d %H:%M')
        time_remaining = end_time - datetime.now()
        if time_remaining <= timedelta(seconds=0) and auction['highest_bidder_id'] == user['id']:
            data = f"Bidding for this auction has ended.\nThis item is Sold to you with last price {auction['highest_bid']}."
            client.client.send(data)
            self.accept_purchase(client.user_id, auction['highest_bid'])
            self.remove_client(client)
        elif time_remaining <= timedelta(seconds=0):
            data = f"Bidding for this auction has ended.\nThis item is Sold to {auction['highest_bidder']} with last price {auction['highest_bid']}."
            client.client.send(data)
            self.remove_client(client)

    def accept_purchase(self, user_id: int, bid_amount: int):
        try:
            users = self.load_data(USERS_FILE)
            users[user_id - 1]['balance'] = users[user_id - 1]['balance'] - bid_amount
            self.save_data(USERS_FILE, users)
        except Exception as e:
            print(e)

    def remove_client(self, client: ClientModel):
        self.live_update_clients.discard(client)

    def broadcast_loop(self):
        while True:
            time.sleep(1)  # Update every 5 seconds
            self.send_winner_thread()
            if self.update_item is not None:
                self.broadcast_thread(self.update_item)
                self.update_item = None
                print("-Loop start-")

    def start(self):
        print('[INFO] Server listening ...')
        loop_broadcast = threading.Thread(target=self.broadcast_loop)
        loop_broadcast.start()
        while True:
            client_socket, addr = self.server.accept()
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    @staticmethod
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

    def handle_live(self, client: Server, auction_id: int, user_id: int):
        auctions = self.load_data(AUCTIONS_FILE)
        if auction_id <= 0 or auction_id > len(auctions):
            print("Invalid auction ID.")
            client.send("INVALID ID")
            return

        auction = auctions[auction_id - 1]
        end_time = datetime.strptime(auction['end_time'], '%Y-%m-%d %H:%M')
        time_remaining = end_time - datetime.now()
        print(f"Title:{auction['title']}")
        if time_remaining <= timedelta(seconds=0):
            print(f"Bidding for this auction has ended.\nThis item is Sold to {auction['highest_bidder']}.")
            client.send(f"Bidding for this auction has ended.\nThis item is Sold to {auction['highest_bidder']}.")
            return
        data = f"Time Remaining: {self.cal_time_remain(time_remaining)}\n"
        print(f"Time Remaining: {self.cal_time_remain(time_remaining)}")
        data += f"Highest Bid: {auction['highest_bid']} by {auction['highest_bidder']}" if auction[
                                                                                               'highest_bidder'] is not None else f"Base price: {auction['base_price']} by {auction['seller']}"
        print(data)

        update_item = {"item_id": auction_id, "user_id": user_id, "msg": data, "from": "live"}
        clientModel = ClientModel(client, auction_id, user_id)
        self.update_item = update_item
        if len(self.live_update_clients) == 0:
            self.live_update_clients.add(clientModel)

        else:
            "" if self.has_client(client, auction_id) else self.live_update_clients.add(clientModel)

    def has_client(self, client: Server, item_id: int):
        for clientModel in self.live_update_clients:
            if clientModel.client == client:
                clientModel.item_id = item_id
                # self.live_update_clients.update(clientModel)
                return True
        return False

    # Function to load data from a file
    @staticmethod
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
    @staticmethod
    def save_data(file_name, data):
        """
        Save data to a JSON file.

        Parameters:
            file_name (str): The name of the file to save to.
            data (list): The data to be saved.

        Returns:
            None
        """
        try:
            with open(file_name, 'w') as file:
                json.dump(data, file, indent=2)
            return True
        except Exception as e:
            return False

    def filter_auctions(self, ended=False):
        """
        Fileter the auctions base the end status
        Parameters:
            ended (boolean) :True to filer ended auction,Default  not filtered
        Returns:
            List : the filtered auctions
        """
        auctions = self.load_data(AUCTIONS_FILE)
        filtered_auctions = []
        for auction in auctions:
            end_time = datetime.strptime(auction['end_time'], '%Y-%m-%d %H:%M')
            time_remaining = end_time - datetime.now()
            filtered_auctions.append(
                auction) if ended and time_remaining.total_seconds() > 0 else filtered_auctions.append(
                auction) if not ended and not time_remaining.total_seconds() > 0 else ""
        return filtered_auctions

    def add_user(self, data):
        users = self.load_data(USERS_FILE)
        user = json.loads(data.replace("'", "\""))
        new_user = {"id": len(users) + 1, "username": user["username"], "email": user["email"],
                    "password": user["password"], "contact": user["contact"], "balance": user["balance"]}
        users.append(new_user)
        return self.save_data(USERS_FILE, users)

    def check_email(self, email: str):
        users: list = self.load_data(USERS_FILE)
        check = next((user for user in users if user['email'] == email), False)
        print(check)
        return check


if __name__ == "__main__":
    init_db()
    server = AuctionServer()
    server.start()
