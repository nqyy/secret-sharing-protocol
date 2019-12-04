# Referenced and modified from: https://github.com/Legrandin/pycryptodome/blob/master/lib/Crypto/Protocol/SecretSharing.py
from Crypto.Util import number
from Crypto.Util.number import long_to_bytes, bytes_to_long
from Crypto.Random import get_random_bytes as rng


def ss_encode(val):
    return number.long_to_bytes(val, 16)


def ss_decode(val):
    return number.bytes_to_long(val)


def _mult_gf2(f1, f2):
    """Multiply two polynomials in GF(2)"""

    # Ensure f2 is the smallest
    if f2 > f1:
        f1, f2 = f2, f1
    z = 0
    while f2:
        if f2 & 1:
            z ^= f1
        f1 <<= 1
        f2 >>= 1
    return z


def _div_gf2(a, b):
    """
    Compute division of polynomials over GF(2).
    Given a and b, it finds two polynomials q and r such that:

    a = b*q + r with deg(r)<deg(b)
    """

    if (a < b):
        return 0, a

    deg = number.size
    q = 0
    r = a
    d = deg(b)
    while deg(r) >= d:
        s = 1 << (deg(r) - d)
        q ^= s
        r ^= _mult_gf2(b, s)
    return (q, r)


class _Element(object):
    """Element of GF(2^128) field"""

    # The irreducible polynomial defining this field is 1+x+x^2+x^7+x^128
    irr_poly = 1 + 2 + 4 + 128 + 2 ** 128

    def __init__(self, encoded_value):
        """Initialize the element to a certain value.

        The value passed as parameter is internally encoded as
        a 128-bit integer, where each bit represents a polynomial
        coefficient. The LSB is the constant coefficient.
        """
        if isinstance(encoded_value, int):
            self._value = encoded_value
        elif len(encoded_value) == 16:
            self._value = bytes_to_long(encoded_value)
        else:
            raise ValueError(
                "The encoded value must be an integer or a 16 byte string")

    def __int__(self):
        """Return the field element, encoded as a 128-bit integer."""
        return self._value

    def encode(self):
        """Return the field element, encoded as a 16 byte string."""
        return long_to_bytes(self._value, 16)

    def __mul__(self, factor):

        f1 = self._value
        f2 = factor._value

        # Make sure that f2 is the smallest, to speed up the loop
        if f2 > f1:
            f1, f2 = f2, f1

        if self.irr_poly in (f1, f2):
            return _Element(0)
        mask1 = 2 ** 128
        v, z = f1, 0
        while f2:
            if f2 & 1:
                z ^= v
            v <<= 1
            if v & mask1:
                v ^= self.irr_poly
            f2 >>= 1
        return _Element(z)

    def __add__(self, term):
        return _Element(self._value ^ term._value)

    def inverse(self):
        """Return the inverse of this element in GF(2^128)."""
        r0, r1 = self._value, self.irr_poly
        s0, s1 = 1, 0
        while r1 > 0:
            q = _div_gf2(r0, r1)[0]
            r0, r1 = r1, r0 ^ _mult_gf2(q, r1)
            s0, s1 = s1, s0 ^ _mult_gf2(q, s1)
        return _Element(s0)


class SecretSharing(object):
    @staticmethod
    def split(k, n, secret):
        """Split a secret into *n* shares.

        The secret can be reconstructed later when *k* shares
        out of the original *n* are recombined. Each share
        must be kept confidential to the person it was
        assigned to.

        Each share is associated to an index (starting from 1),
        which must be presented when the secret is recombined.

        Args:
          k (integer):
            The number of shares that must be present in order to reconstruct
            the secret.
          n (integer):
            The total number of shares to create (larger than *k*).
          secret (byte string):
            The 16 byte string (e.g. the AES128 key) to split.

        Return:
            *n* tuples, each containing the unique index (an integer) and
            the share (a byte string, 16 bytes long) meant for a
            participant.
        """
        coeffs = [_Element(rng(16)) for i in range(k - 1)]
        coeffs.insert(0, _Element(secret))

        def make_share(user, coeffs):
            share, x, idx = [_Element(p) for p in (0, 1, user)]
            for coeff in coeffs:
                share += coeff * x
                x *= idx
            return share.encode()

        return [(i, make_share(i, coeffs)) for i in range(1, n + 1)]

    @staticmethod
    def combine(shares):
        """Recombine a secret, if enough shares are presented.

        Args:
          shares (tuples):
            At least *k* tuples, each containin the index (an integer) and
            the share (a byte string, 16 bytes long) that were assigned to
            a participant.

        Return:
            The original secret, as a byte string (16 bytes long).
        """
        shares = [[_Element(y) for y in x] for x in shares]

        result = _Element(0)
        k = len(shares)
        for j in range(k):
            x_j, y_j = shares[j]

            coeff_0_l = _Element(0)
            while not int(coeff_0_l):
                coeff_0_l = _Element(rng(16))
            inv = coeff_0_l.inverse()

            for m in range(k):
                x_m = shares[m][0]
                if m != j:
                    t = x_m * (x_j + x_m).inverse()
                    coeff_0_l *= t
            result += y_j * coeff_0_l * inv
        return result.encode()
