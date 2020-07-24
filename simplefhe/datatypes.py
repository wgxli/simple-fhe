from seal import Ciphertext, Plaintext

import simplefhe


class EncryptedValue:
    def __init__(self, value):
        if isinstance(value, EncryptedValue): value = value._ciphertext
        if not isinstance(value, Ciphertext):
            value = simplefhe.encrypt(value)._ciphertext

        self._ciphertext = value
        self._mode = simplefhe._mode


    def _binop(
        self, other,
        cipher_func, plain_func = None,
        _is_mult: bool = False
    ):
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


        # Must normalize floats to same scale before adding/subtracting
        float_mode = (simplefhe._mode['type'] == 'float')
        evaluator = simplefhe._evaluator

        # If adding, we need to match scale and modulus
        if float_mode and not _is_mult:
            target_scale = simplefhe._mode['default_scale']
            self._ciphertext.scale(target_scale)
            parms = self._ciphertext.parms_id()
            def normalize(x):
                simplefhe._evaluator.mod_switch_to_inplace(x, parms)

        # After each multiplication, we should relinearize
        def renormalize(x):
            if float_mode and _is_mult:
                evaluator.relinearize_inplace(x, simplefhe._relin_key)
                evaluator.rescale_to_next_inplace(x)

        # Determine type of other operand
        if not isinstance(other, Ciphertext):
            from simplefhe.encryptors import encode_item
            if False:#plain_func is not None:
                # Use plain_func for performance
                pt = encode_item(other)
                if float_mode and not _is_mult: normalize(pt)
                plain_func(self._ciphertext, pt, result)
                renormalize(result)
                return EncryptedValue(result)
            else:
                # Fallback to encrypting and using cipher_func
                other = simplefhe.encrypt(other)._ciphertext

        # If adding, we need to match scale and modulus
        if float_mode and not _is_mult:
            other.scale(target_scale)
            normalize(other)

        # Compute binary operation
        cipher_func(self._ciphertext, other, result)

        renormalize(result)
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
            simplefhe._evaluator.multiply_plain,
            _is_mult = True
        )

    __radd__ = __add__
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
