import base64
import hashlib
import os

def random_challenge():
    return hashlib.sha256(os.urandom(16)).digest()

def to_buffer(txt):
    return bytearray(txt, 'utf-8')

def parse_buffer(buffer):
    return buffer.decode('utf-8')

def is_base64url(txt):
    try:
        base64.b64decode(txt, validate=True)
        return True
    except:
        return False

def to_base64url(buffer):
    txt = base64.b64encode(buffer).decode('utf-8')
    return txt.replace('+', '-').replace('/', '_').rstrip('=')

def parse_base64url(txt):
    txt = txt.replace('-', '+').replace('_', '/') + '=' * (4 - len(txt) % 4) 
    return base64.b64decode(txt)

def sha256(buffer):
    return hashlib.sha256(buffer).digest()

def buffer_to_hex(buffer):
    return buffer.hex()

def concatenate_buffers(buffer1, buffer2):
    return buffer1 + buffer2

