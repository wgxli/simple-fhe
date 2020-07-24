from seal import Plaintext, Ciphertext

import simplefhe


def decrypt(item):
    decryptor = simplefhe._decryptor
    if decryptor is None:
        raise ValueError('Private key has not been set. Decryption not possible.')

    result = Plaintext()
    decryptor.decrypt(item._ciphertext, result)
    result = result.to_string()

    mode = simplefhe._mode
    if mode['type'] == 'int':
        result = int(result, 16) 
        if result > mode['modulus'] // 2:
            result -= mode['modulus']
        return result
    else:
        return float(result)
