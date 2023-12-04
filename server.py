import random
from socket import socket


class Server:
    def __init__(self, client_socket: socket):
        self.client: socket = client_socket
        self.randomKey = random.randint(10000, 999999)
        self.encrypted_data = ''

    def start_encryption(self, text, key):
        """
        Encrypts the given text using XOR operations with the provided key.

        Parameters:
        - text: str, the text to be encrypted.
        - key: str, the encryption key.

        Returns:
        - str, the encrypted data.
        """
        self.encrypted_data = ''
        totalKey = sum(ord(char) for char in key)

        for char in text:
            encrypted_ord = ord(char) ^ totalKey
            double_encrypted_ord = encrypted_ord ^ self.randomKey
            double_encrypted_binary = format(double_encrypted_ord, '016b')
            self.encrypted_data += self.binary_to_original(double_encrypted_binary)

        totalKey_binary = bin(totalKey)[2:]
        randomKey_binary = bin(self.randomKey)[2:]
        self.encrypted_data += "X" + totalKey_binary + 'X' + randomKey_binary
        return self.encrypted_data

    def ensure_multiple_of_eight(self, binary_str):
        """
        Ensures the binary string length is a multiple of eight by adding zeros.

        Parameters:
        - binary_str: str, the binary string to be padded.

        Returns:
        - str, the padded binary string.
        """
        remainder = len(binary_str) % 16

        if remainder != 0:
            zeros_needed = 16 - remainder
            binary_str += '0' * zeros_needed

        return binary_str

    def binary_to_original(self, binary_str):
        """
        Converts a binary string to its original form (char by default).

        Parameters:
        - binary_str: str, the binary string to be converted.
        - output_type: str, the type of output ('char' by default).

        Returns:
        - str, the original value.
        """
        decimal_value = int(binary_str, 2)
        original_value = chr(decimal_value)
        return original_value

    def startDecryption(self, encrypted_data):
        """
        Alternative decryption method using binary operations.

        Parameters:
        - encrypted_data: str, the encrypted data to be decrypted.

        Returns:
        - str, the decrypted data.
        """
        decrypted_text = ''
        parts = encrypted_data.split('X')
        totalKey = int(parts[-2], 2)
        randomKey = int(parts[-1], 2)
        for part in parts[0]:
            double_encrypted_ord = int(self.original_to_binary(part), 2)
            encrypted_ord = double_encrypted_ord ^ randomKey
            char = chr(encrypted_ord ^ totalKey)

            decrypted_text += char
        return decrypted_text

    def original_to_binary(self, original_value, input_type='char'):
        """
        Converts original values (characters by default) to binary.

        Parameters:
        - original_value: str, the original value to be converted.
        - input_type: str, the type of input ('char' by default).

        Returns:
        - str, the binary representation of the original value.
        """
        binary_result = ""
        for i in original_value:
            binary_result += format(ord(i), "08b")
        return binary_result

    def original_to_binary(self, original_value, input_type='char'):
        binary_result = ""
        for i in original_value:
            binary_result += format(ord(i), "08b")
        return binary_result

    def decrypt(self, encrypted_data: str):
        return self.startDecryption(encrypted_data)

    def encrypt(self, data: str, key: str):
        return self.start_encryption(data, key)

    def send(self, msg: str):
        print(msg)
        data = self.encrypt(msg, "server secret key").encode("utf-8")
        print(len(data))
        self.client.sendall(data)

    def recv(self):
        data = self.client.recv(1024)
        return self.decrypt(data.decode('utf-8'))
