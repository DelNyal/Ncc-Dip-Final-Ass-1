
import random

class A3Encryption:
    def __init__(self):
        """
        A3Encryption class for text encryption using bitwise XOR operations.

        Attributes:
        - encrypted_data: str, stores the encrypted data.
        - randomKey: int, a random key for additional encryption.
        """
        self.encrypted_data = ''
        self.randomKey = random.randint(10000, 99999)

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

    def split_and_pad(self, binary_str):
        """
        Splits the binary string into groups of eight and pads if necessary.

        Parameters:
        - binary_str: str, the binary string to be split.

        Returns:
        - list, a list of binary strings representing groups of eight.
        """
        binary_str = self.ensure_multiple_of_eight(binary_str)
        groups_of_eight = []
        for i in range(0, len(binary_str), 8):
            group = binary_str[i:i + 8]
            res = self.binary_to_original(group)
            groups_of_eight.append(res)
        return groups_of_eight

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


class A3Decryption:
    def __init__(self):
        """
        A3Decryption class for decrypting text encrypted with A3Encryption.

        Attributes:
        - dataList: list, stores the encrypted data split into parts.
        - decrypted_data: str, stores the decrypted data.
        """
        self.dataList: list = []
        self.decrypted_data: str = ''

    def start_Decryption(self, encrypted_data: str):
        """
        Decrypts the given encrypted data using XOR operations with keys.

        Parameters:
        - encrypted_data: str, the encrypted data to be decrypted.

        Returns:
        - str, the decrypted data.
        """
        self.decrypted_data: str = ''
        self.dataList = encrypted_data.split('X')
        keyList = self.dataList[-2:]
        key = int(keyList[0], 16)  # dec
        rKey = int(keyList[1], 16)

        for i in range(len(self.dataList) - 2):
            dDecrypt: int = int(self.dataList[i], 16) ^ rKey

            decrypted_int = dDecrypt ^ key
            self.decrypted_data += chr(decrypted_int)

        return self.decrypted_data

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



if __name__ == "__main__":
    a3 = A3Encryption()
    da3 = A3Decryption()
    message = "[{\"data\":\"This is secret message from server\", \"key\":\"jhfjahdfjh kjhdfkjahfjkha\", \"user\": \"mg mg\",\"data\":{\"data\":\"This is secret message from server\", \"key\":\"jhfjahdfjh kjhdfkjahfjkha\", \"user\": \"mg mg\"}},{\"data\":\"This is secret message from server\", \"key\":\"jhfjahdfjh kjhdfkjahfjkha\", \"user\": \"mg mg\",\"data\":{\"data\":\"This is secret message from server\", \"key\":\"jhfjahdfjh kjhdfkjahfjkha\", \"user\": \"mg mg\"}},{\"data\":\"This is secret message from server\", \"key\":\"jhfjahdfjh kjhdfkjahfjkha\", \"user\": \"mg mg\",\"data\":{\"data\":\"This is secret message from server\", \"key\":\"jhfjahdfjh kjhdfkjahfjkha\", \"user\": \"mg mg\"}},{\"data\":\"This is secret message from server\", \"key\":\"jhfjahdfjh kjhdfkjahfjkha\", \"user\": \"mg mg\",\"data\":{\"data\":\"This is secret message from server\", \"key\":\"jhfjahdfjh kjhdfkjahfjkha\", \"user\": \"mg mg\"}},{\"data\":\"This is secret message from server\", \"key\":\"jhfjahdfjh kjhdfkjahfjkha\", \"user\": \"mg mg\",\"data\":{\"data\":\"This is secret message from server\", \"key\":\"jhfjahdfjh kjhdfkjahfjkha\", \"user\": \"mg mg\"}},{\"data\":\"This is secret message from server\", \"key\":\"jhfjahdfjh kjhdfkjahfjkha\", \"user\": \"mg mg\",\"data\":{\"data\":\"This is secret message from server\", \"key\":\"jhfjahdfjh kjhdfkjahfjkha\", \"user\": \"mg mg\"}}]"
    encrypted: str = a3.start_encryption(message, "secret key")
    print("Encrypted data:" + encrypted)
    print(f"Size:{len(encrypted.encode('utf-8'))}")
    decrypted: str = da3.startDecryption(encrypted)
    print("Decrypted data:", decrypted)
    print(f"Size:{len(decrypted.encode('utf-8'))}")
