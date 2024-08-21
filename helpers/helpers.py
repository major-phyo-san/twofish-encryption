import base64
import random
import string

def pad(data, block_size):
        pad_len = block_size - (len(data) % block_size)
        padding = bytes([pad_len]) * pad_len
        return data + padding

def unpad(data, block_size):
    padding_len = data[-1]
    if padding_len > block_size:
        raise ValueError("Invalid padding length")
    return data[:-padding_len]

def convert_to_bytes(base64_string):
        return base64.b64decode(base64_string)
    
def convert_to_b64str(bytes):
    return base64.b64encode(bytes).decode('utf-8')

def convert_to_str(bytes):
    return bytes.decode("utf-8")

def convert_string_to_key(keystring):
    binary_str = ''.join(format(ord(i), '08b') for i in keystring)
    integer_value = int(binary_str, 2)
    byte_length = (len(binary_str) + 7) // 8
    key = integer_value.to_bytes(byte_length, byteorder='big')
    base64_string = convert_to_b64str(key)
    return base64_string

def generate_random_string(length):
    # Use string.ascii_letters for both uppercase and lowercase letters
    # Use string.digits for numbers
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string
