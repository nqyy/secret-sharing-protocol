
import os
import random
import struct
from Crypto.Cipher import AES


def encrypt_file(key, in_filename, out_filename):
    iv = os.urandom(16)
    encryptor = AES.new(key, AES.MODE_CFB, IV=iv)

    fi = open(in_filename, "rb")
    ciphertext = encryptor.encrypt(fi.read())

    fo = open(out_filename, "wb")
    fo.write(iv + ciphertext)


def decrypt_file(key, in_filename, out_filename):
    fi = open(in_filename, "rb")
    iv = fi.read(16)
    decryptor = AES.new(key, AES.MODE_CFB, IV=iv)
    plain = decryptor.decrypt(fi.read())

    fo = open(out_filename, "wb")
    fo.write(plain)
