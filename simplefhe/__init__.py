import sys
from typing import Tuple, Optional
import types

try:
    from seal import *
except ModuleNotFoundError:
    raise ModuleNotFoundError('simplefhe depends on the SEAL-Python library. See https://github.com/Huelse/SEAL-Python for installation instructions.')


PrivateKey = SecretKey

_public_key: Optional[PublicKey] = None
_private_key: Optional[PrivateKey] = None
_relin_key: Optional[RelinKeys] = None

_mode = None
_context = None
_encryptor = None
_decryptor = None
_evaluator = None



def set_public_key(key: PublicKey) -> None:
    global _public_key, _encryptor
    _public_key = key
    if key is None:
        _encryptor = None
    else:
        _encryptor = Encryptor(_context, key)


def set_private_key(key: PrivateKey) -> None:
    global _private_key, _decryptor
    _private_key = key
    if key is None:
        _decryptor = None
    else:
        _decryptor = Decryptor(_context, key)

def set_relin_key(key: RelinKeys) -> None:
    if _mode['type'] != 'float':
        raise ValueError('relin key should only be set for float mode!')
    global _relin_key
    _relin_key = key


def load_public_key(filepath: str) -> None:
    key = PublicKey()
    key.load(_context, filepath)
    set_public_key(key)


def load_private_key(filepath: str) -> None:
    key = PrivateKey()
    key.load(_context, filepath)
    set_private_key(key)

def load_relin_key(filepath: str) -> None:
    key = RelinKeys()
    key.load(_context, filepath)
    set_relin_key(key)


def initialize(
    mode: str = 'float',
    max_int: int = 1048576
) -> None:
    """
    Re-initializes the FHE encryption context.
    This must be done before any other operations are performed.

    :param mode:
        Must be `int` or `float`.

    :param max_int:
        Only integers in the range [-max_int + 1, max_int] inclusive
        are representable. If `mode != 'int'`, this option is ignored.
    """
    if mode not in ['int', 'float']:
        raise ValueError("mode must be 'int' or 'float'")

    if mode == 'int':
        parms = EncryptionParameters(scheme_type.BFV)
        poly_modulus_degree = 4096
        parms.set_poly_modulus_degree(poly_modulus_degree)
        parms.set_coeff_modulus(CoeffModulus.BFVDefault(poly_modulus_degree))
        parms.set_plain_modulus(2 * max_int)
    else:
        parms = EncryptionParameters(scheme_type.CKKS)
        poly_modulus_degree = 8192 
        parms.set_poly_modulus_degree(poly_modulus_degree)
        parms.set_coeff_modulus(CoeffModulus.Create(
            poly_modulus_degree, [60, 40, 40, 60]
        ))


    # Initialize new context
    global _context, _evaluator, _mode
    _context = SEALContext.Create(parms)
    _evaluator = Evaluator(_context)
    _mode = {'type': mode}
    set_public_key(None)
    set_private_key(None)

    if mode == 'int':
        _mode['modulus'] = 2 * max_int
    else:
        _mode['encoder'] = CKKSEncoder(_context)
        _mode['default_scale'] = pow(2.0, 40)


def generate_keypair() -> Tuple[PublicKey, PrivateKey]:
    """
    Returns a random keypair (public, private).
    If float mode has been set, return three keys
    (public, private, relin).
    """
    keygen = KeyGenerator(_context)
    if _mode['type'] != 'float':
        return (keygen.public_key(), keygen.secret_key())
    else:
        return (keygen.public_key(), keygen.secret_key(), keygen.relin_keys())


def display_config() -> None:
    """Displays the current config to STDOUT."""
    print('===== simplefhe config =====' )
    int_mode = (_mode['type'] == 'int')

    if int_mode:
        modulus = _mode['modulus']
        print('mode: integer (exact)')
        print(f'min_int: {-modulus//2 + 1}')
        print(f'max_int: {modulus//2}')
    else:
        print('mode: float (approximate)')

    is_initialized = lambda key: 'missing' if _public_key is None else 'initialized'

    print(f'public_key: {is_initialized(_public_key)}')
    print(f'private_key: {is_initialized(_private_key)}')
    if not int_mode:
        print(f'relin_keys: {is_initialized(_relin_key)}')
    print()



initialize('int')

from simplefhe.encryptors import encrypt
from simplefhe.decryptors import decrypt
from simplefhe.datatypes import load_encrypted_value
