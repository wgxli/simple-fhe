from seal import Plaintext, Ciphertext

import simplefhe

from simplefhe.datatypes import EncryptedValue


def encrypt(item):
    encryptor = simplefhe._encryptor
    if encryptor is None:
        raise ValueError('Public key has not been set. Encryption not possible.')

    # Generate plaintext
    mode = simplefhe._mode
    if mode['type'] == 'int':
        # Encrypt as integer
        modulus = mode['modulus']

        if item <= -modulus//2 or item > modulus//2:
            raise ValueError(
                f'Integer {item} is too large to be represented.'
                + ' Try increasing `max_int` during initialization.'
            )

        item = item % modulus
        item_str = hex(item)[2:]
    else:
        # Encrypt as float
        item_str = str(item)
    pt = Plaintext(item_str)

    # Return encrypted result
    output = Ciphertext()
    encryptor.encrypt(pt, output)
    return EncryptedValue(output)
