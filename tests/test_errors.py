import unittest
import random

from simplefhe import (
    initialize,
    encrypt, decrypt,
    generate_keypair,
    set_public_key, set_private_key, set_relin_key,
    display_config
)


class test_initialize(unittest.TestCase):
    def test_mode_error(self):
        initialize('int')
        self.assertRaises(ValueError, initialize, 'asdf')


class test_int(unittest.TestCase):
    def setUp(self):
        initialize('int')

    def test_public_key_error(self):
        self.assertRaises(ValueError, encrypt, 1)

    def test_key_type_error(self):
        public_key, private_key = generate_keypair()
        self.assertRaises(AssertionError, set_public_key, private_key)
        self.assertRaises(AssertionError, set_private_key, public_key)
        self.assertRaises(AssertionError, set_relin_key, public_key)

    def test_private_key_error(self):
        public_key, _ = generate_keypair()
        set_public_key(public_key)
        a = encrypt(1)
        self.assertRaises(ValueError, decrypt, a)

    def test_relin_key_error(self):
        initialize('float')
        _, _, relin_key = generate_keypair()
        initialize('int')
        self.assertRaises(ValueError, set_relin_key, relin_key)

    def test_float_error(self):
        public_key, private_key = generate_keypair()
        set_public_key(public_key)
        set_private_key(private_key)
        decrypt(encrypt(1))
        self.assertRaises(ValueError, encrypt, 1.2)


    def test_overflow(self):
        public_key, private_key = generate_keypair()
        set_public_key(public_key)
        set_private_key(private_key)
        encrypt(100)
        self.assertRaises(ValueError, encrypt, pow(2, 30))
        self.assertRaises(ValueError, encrypt, -pow(2, 30))


class test_float(unittest.TestCase):
    def setUp(self):
        initialize('float')

    def test_public_key_error(self):
        self.assertRaises(ValueError, encrypt, 1)

    def test_private_key_error(self):
        public_key, _, relin_key = generate_keypair()
        set_public_key(public_key)
        set_relin_key(relin_key)
        a = encrypt(1)
        self.assertRaises(ValueError, decrypt, a)

    def test_relin_key_error(self):
        public_key, private_key, relin_key = generate_keypair()
        set_public_key(public_key)
        self.assertRaises(ValueError, encrypt, 1)
        set_private_key(private_key)
        self.assertRaises(ValueError, encrypt, 1)

        set_relin_key(relin_key)
        a = encrypt(1)
        decrypt(a)
        set_relin_key(None)
        self.assertRaises(ValueError, decrypt, a)
