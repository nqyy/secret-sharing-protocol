import binascii
from secret_sharing import SecretSharing
import Crypto

def ss_encode(val):
    return Crypto.Util.number.long_to_bytes(val, 16)

def ss_decode(val):
    return Crypto.Util.number.bytes_to_long(val)

# dealer
key = 123 # the secret to share
n = 5 # how many shares
k = 3 # how many people can reconstruct the secret
shares = SecretSharing.split(k, n, key)
for idx, share in shares:
    print("Share #%d: %s" % (idx, binascii.hexlify(share)))
    print(ss_decode(share))

# construct back
key = SecretSharing.combine(shares)
result = ss_decode(key)
print(result)
