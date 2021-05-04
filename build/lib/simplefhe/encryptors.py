from seal import Plaintext, Ciphertext

import simplefhe

from simplefhe.datatypes import EncryptedValue


def encrypt(item) -> EncryptedValue:
    encryptor = simplefhe._encryptor

    if encryptor is None:
        raise ValueError('Public key has not been set. Encryption not possible.')

    if simplefhe._relin_keys is None:
        raise ValueError('Relinearization keys have not been set. Encryption not possible.')

    # Generate plaintext
    pt = encode_item(item)

    # Return encrypted result
    output = encryptor.encrypt(pt)
    return EncryptedValue(output)


def encode_item(item) -> Plaintext:
    """Encode the given item to plaintext, depending on the current mode."""
    if simplefhe._mode['type'] == 'int':
        if isinstance(item, float):
            raise ValueError('Float computations require floating point mode to be enabled.')
        else:
            return encode_int(item)
    else:
        # Encrypt as float
        return encode_float(item)


def encode_int(item: int) -> Plaintext:
    """Encodes the given integer into a plaintext."""
    modulus = simplefhe._mode['modulus']

    if item <= -modulus//2 or item > modulus//2:
        raise ValueError(
            f'Integer {item} is too large to be represented.'
            + ' Try increasing `max_int` during initialization.'
        )

    item = item % modulus
    item_str = hex(item)[2:]
    return Plaintext(item_str)


def encode_float(item: float) -> Plaintext:
    """Encodes the given float into a plaintext.""" 
    mode = simplefhe._mode
    encoder = mode['encoder']
    scale = mode['default_scale']
    
    output = encoder.encode(float(item), scale)
    return output
