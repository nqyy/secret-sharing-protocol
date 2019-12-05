import inspect
import sys

IDENTIFIER_LENGTH = 5
# supported_cls = []

class MessageManager:
    """
    Message Manager
    get_identifier: input a valid class, get's its identifier
    encode: enter a class and items, encode the bytestring for you
    decode: enter a bytestring, decode the bytestring into (cls, items) for you
    typed_decode: enter a class and bytestring, check if class matches and decode the string for you.
    """

    @staticmethod
    def get_identifier(cls):
        assert len(cls.identifier()) == IDENTIFIER_LENGTH
        return cls.identifier()

    @staticmethod
    def encode(cls, *args):
        identifier = MessageManager.get_identifier(cls)
        return identifier+(cls.encode(*args) if hasattr(cls, 'encode') else b'')

    @staticmethod
    def decode(bytestring):
        identifier = bytestring[:IDENTIFIER_LENGTH]
        bytestring = bytestring[IDENTIFIER_LENGTH:]

        possible = []
        for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass):
            if hasattr(obj, 'identifier') and identifier == obj.identifier():
                possible.append(obj)
        if len(possible) == 0:
            raise ValueError('Unidentified Message Type')
        if len(possible) > 1:
            raise ValueError('Ambiguous class Types')

        cls = possible[0]
        if not hasattr(cls, 'decode'):
            return cls, None

        return cls, cls.decode(bytestring)

    @staticmethod
    def typed_decode(target_cls, bytestring):
        cls, res = MessageManager.decode(bytestring)
        assert cls == target_cls, 'Get MessageType: {}, expected: {}'.format(cls, target_cls)
        return res


"""
Message classes
encode: encode all data from input and return bytestring based on it (can choose not define it which defaults to empty)
decode: decode all data from bytestring and return original input (can choose not define it which defaults to None)
"""

class AssignMessage:
    @staticmethod
    def identifier():
        return b'ASSIG'

    @staticmethod
    def encode(ix, secret):
        return secret+str(ix).encode()

    @staticmethod
    def decode(bytestring):
        return int(bytestring[16:].decode()), bytestring[:16]


class AckMessage:
    @staticmethod
    def identifier():
        return b'ACK--'

class DealerExitMessage:
    @staticmethod
    def identifier():
        return b'EXIT-'

class RequestMessage:
    @staticmethod
    def identifier():
        return b'Reqst'


class ShareMessage:
    @staticmethod
    def identifier():
        return b'SHARE'

    @staticmethod
    def encode(ix, secret):
        return secret+str(ix).encode()

    @staticmethod
    def decode(bytestring):
        return int(bytestring[16:].decode()), bytestring[:16]


