import unittest
import random

from simplefhe import (
    initialize,
    encrypt, decrypt,
    generate_keypair,
    set_public_key, set_private_key, set_relin_key
)

ITERATIONS = 50


class test_int(unittest.TestCase):
    def setUp(self):
        initialize('int')
        pub, priv = generate_keypair()
        set_public_key(pub)
        set_private_key(priv)

    def randint(self):
        return random.randint(-1000, 1000)

    def test_addition(self):
        for i in range(ITERATIONS):
            a = self.randint()
            b = self.randint()
            self.assertEqual(decrypt(encrypt(a) + encrypt(b)), a + b)

    def test_multiplication(self):
        for i in range(ITERATIONS):
            a = self.randint()
            b = self.randint()
            self.assertEqual(decrypt(encrypt(a) * encrypt(b)), a * b)

    def test_running_sum(self):
        true = 0
        target = 0
        for i in range(ITERATIONS):
            x = self.randint()
            true += x
            target += encrypt(x)
        self.assertEqual(decrypt(target), true)


class test_float(unittest.TestCase):
    def setUp(self):
        initialize('float')
        pub, priv, relin = generate_keypair()
        set_public_key(pub)
        set_private_key(priv)
        set_relin_key(relin)

    def rand(self):
        return random.gauss(0, 1000)

    def test_addition(self):
        for i in range(ITERATIONS):
            a = self.rand()
            b = self.rand()
            self.assertAlmostEqual(decrypt(encrypt(a) + encrypt(b)), a + b)

    def test_multiplication(self):
        for i in range(ITERATIONS):
            a = self.rand()
            b = self.rand()
            self.assertAlmostEqual(decrypt(encrypt(a) * encrypt(b)), a * b, places=3)

    def test_running_sum(self):
        true = 0
        target = 0
        for i in range(ITERATIONS):
            x = self.rand()
            true += x
            target += encrypt(x)
        self.assertAlmostEqual(decrypt(target), true, places=3)
