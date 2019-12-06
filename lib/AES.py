
# Methods used for AES encryption and decryption.
import os
import random
import struct
from Crypto.Cipher import AES


def encrypt_file(key, in_filename, out_filename):
    '''
    AES encrypt the input file using provided key
    output encrypted file
    Args:
        key: 16 byte AES key
        in_filename: input secret file name
        out_filename: output file name
    '''
    iv = os.urandom(16)
    encryptor = AES.new(key, AES.MODE_CFB, IV=iv)

    fi = open(in_filename, "rb")
    ciphertext = encryptor.encrypt(fi.read())

    if not os.path.exists(os.path.dirname(out_filename)):
        os.makedirs(os.path.dirname(out_filename))

    fo = open(out_filename, "wb")
    fo.write(iv + ciphertext)


def decrypt_file(key, in_filename, out_filename):
    '''
    AES decrypt the input file using provided key
    output decrypted file
    Args:
        key: 16 byte AES key
        in_filename: input encrypted file name
        out_filename: output decrypted file name
    '''
    fi = open(in_filename, "rb")
    iv = fi.read(16)
    decryptor = AES.new(key, AES.MODE_CFB, IV=iv)
    plain = decryptor.decrypt(fi.read())

    if not os.path.exists(os.path.dirname(out_filename)):
        os.makedirs(os.path.dirname(out_filename))

    fo = open(out_filename, "wb")
    fo.write(plain)
