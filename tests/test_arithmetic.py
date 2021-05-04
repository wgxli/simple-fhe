import unittest
import random
import operator as op

from simplefhe import (
    initialize,
    encrypt, decrypt,
    generate_keypair,
    set_public_key, set_private_key, set_relin_keys,
    display_config
)

ITERATIONS = 25


class test_int(unittest.TestCase):
    def setUp(self):
        initialize('int')
        pub, priv, relin = generate_keypair()
        set_public_key(pub)
        set_private_key(priv)
        set_relin_keys(relin)

        display_config()

    def randint(self):
        return random.randint(-500, 500)

    def binop_test(self, binop):
        for i in range(ITERATIONS):
            a = self.randint()
            b = self.randint()
            self.assertEqual(decrypt(binop(encrypt(a), encrypt(b))), binop(a, b))

    def test_addition(self): self.binop_test(op.add)
    def test_subtraction(self): self.binop_test(op.sub)
    def test_multiplication(self): self.binop_test(op.mul)

    def test_pow(self):
        for i in range(ITERATIONS):
            a = random.randint(-7, 7)
            b = random.randint(0, 6)
            self.assertEqual(decrypt(encrypt(a)**b), a**b)

    def test_pow_error(self):
        a = lambda: encrypt(3)**-1
        self.assertRaises(TypeError, a)

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
        set_relin_keys(relin)

        display_config()

    def rand(self):
        return random.gauss(0, 1000)

    def binop_test(self, binop):
        for i in range(ITERATIONS):
            a = self.rand()
            b = self.rand()
            self.assertAlmostEqual(
                decrypt(binop(encrypt(a), encrypt(b))), binop(a, b),
                places=3
            )

    def test_addition(self): self.binop_test(op.add)
    def test_subtraction(self): self.binop_test(op.sub)
    def test_multiplication(self): self.binop_test(op.mul)

    def test_div(self):
        for i in range(ITERATIONS):
            a = self.rand()
            b = (2 * random.randint(0, 1) - 1) * random.uniform(1, 100)
            self.assertAlmostEqual(
                decrypt(encrypt(a)/b), a/b,
                places=3
            )

    def test_pow(self):
        for i in range(ITERATIONS):
            a = self.rand() / 500
            b = random.randint(0, 4)
            self.assertAlmostEqual(decrypt(encrypt(a)**b), a**b, places=3)

    def test_running_sum(self):
        true = 0
        target = 0
        for i in range(ITERATIONS):
            x = self.rand()
            true += x
            target += encrypt(x)
        self.assertAlmostEqual(decrypt(target), true, places=3)
