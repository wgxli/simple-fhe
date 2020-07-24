from seal import Ciphertext, Plaintext

import simplefhe


class EncryptedValue:
    def __init__(self, value):
        if not isinstance(value, Ciphertext):
            value = simplefhe.encrypt(value)

        self._ciphertext = value
        self._mode = simplefhe._mode


    def _binop(self, other, cipher_func, plain_func = None):
        """
        Returns the result of a binary operation between self and other.
        
        :param cipher_func:
            Must take three Ciphertext arguments.
            The function must apply a binary operation to the
            first two arguments, and overwrite the third argument
            with the result.

        :param plain_func:
            Optional. Used when `other` is an unencrypted value
            for performance improvement.
            If omitted, `other` will be encrypted and passed into
            `cipher_func`.
        """
        result = Ciphertext()
        if isinstance(other, EncryptedValue):
            other = other._ciphertext
        
        if not isinstance(other, Ciphertext):
            if plain_func is not None:
                # Use plain_func for performance
                pt = Plaintext(str(other))
                plain_func(self._ciphertext, pt, result)
                return EncryptedValue(result)
            else:
                # Fallback to encrypting and using cipher_func
                other = simplefhe.encrypt(other)

        cipher_func(self._ciphertext, other, result)
        return EncryptedValue(result)


    # Arithmetic
    def __add__(self, other):
        return self._binop(
            other,
            simplefhe._evaluator.add,
            simplefhe._evaluator.add_plain
        )



    def __sub__(self, other):
        return self._binop(
            other,
            simplefhe._evaluator.sub,
            simplefhe._evaluator.sub_plain
        )


    def __mul__(self, other):
        return self._binop(
            other,
            simplefhe._evaluator.multiply,
            simplefhe._evaluator.multiply_plain
        )

    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__


    def __repr__(self):
        type_string = self._mode['type']
        return f'<encrypted {type_string}>'


    def save(self, filepath: str):
        """Saves this encrypted value to the given file."""
        self._ciphertext.save(filepath)


def load_encrypted_value(filepath: str) -> EncryptedValue:
    """Loads a saved encrypted value from the given file."""
    ciphertext = Ciphertext()
    ciphertext.load(simplefhe._context, filepath)
    return EncryptedValue(ciphertext)
