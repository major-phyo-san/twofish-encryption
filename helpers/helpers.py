import base64

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
