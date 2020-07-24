from seal import Plaintext, Ciphertext, DoubleVector

import simplefhe


def decrypt(item):
    decryptor = simplefhe._decryptor
    if decryptor is None:
        raise ValueError('Private key has not been set. Decryption not possible.')

    result = Plaintext()
    decryptor.decrypt(item._ciphertext, result)

    mode = item._mode
    if mode['type'] == 'int':
        result = result.to_string()
        result = int(result, 16) 
        if result > mode['modulus'] // 2:
            result -= mode['modulus']
        return result
    else:
        decoded = DoubleVector()
        item._mode['encoder'].decode(result, decoded)
        return float(decoded[0])
