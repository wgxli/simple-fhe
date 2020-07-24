import unittest
import random

from simplefhe import (
    initialize,
    encrypt, decrypt,
    generate_keypair,
    set_public_key, set_private_key, set_relin_keys
)
from simplefhe.datatypes import EncryptedValue



class test_init(unittest.TestCase):
    def setUp(self):
        initialize('int')
        pub, priv, relin = generate_keypair()
        set_public_key(pub)
        set_private_key(priv)
        set_relin_keys(relin)

    def test_plaintext_init(self):
        N = 109023
        a = EncryptedValue(N)
        b = EncryptedValue(a)
        self.assertEqual(decrypt(a), N)
        self.assertEqual(decrypt(b), N)

    def test_repr(self):
        a = encrypt(3)
        self.assertEqual(repr(a), '<encrypted int>')
