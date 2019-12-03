from binascii import hexlify
from secret_sharing import SecretSharing

# dealer
key = 0x123 # the secret to share
n = 5 # how many shares
k = 3 # how many people can reconstruct the secret
shares = SecretSharing.split(k, n, key)
for idx, share in shares:
    print("Index #%d: %s" % (idx, hexlify(share)))

# construct back
key = SecretSharing.combine(shares)
print(hexlify(key))
