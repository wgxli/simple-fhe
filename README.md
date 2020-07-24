# A Simple Drop-In Solution for Full Homomorphic Encryption
[![pypi version](https://img.shields.io/pypi/v/simplefhe)](https://pypi.org/project/simplefhe/)
[![build status](https://img.shields.io/travis/wgxli/simple-fhe)](https://travis-ci.org/github/wgxli/simple-fhe)
[![code coverage](https://img.shields.io/coveralls/github/wgxli/simple-fhe)](https://coveralls.io/github/wgxli/simple-fhe)

Full Homomorphic Encryption (FHE) allows untrusted (e.g. cloud) applications
to operate directly on encrypted data, eliminating the need for server-side decryption or trust.

`simplefhe` is a Python library for FHE that intends to be as easy-to-use as possible.
In the simplest case, just a few lines of code are all you need to have working FHE!

## Table of Contents
  * [The Problem](#the-problem)
  * [The Solution](#the-solution)
  * [A More Realistic Example](#a-more-realistic-example)
     * [Step 1: Keypair Generation](#step-1-keypair-generation)
     * [Step 2: Client-Side Encryption](#step-2-client-side-encryption)
     * [Step 3: Server-Side Processing](#step-3-server-side-processing)
     * [Step 4: Client-Side Decryption](#step-4-client-side-decryption)
  * [Installation](#installation)
  * [Notes](#notes)
  * [Floating Point](#floating-point)
  * [Linear Regression](#linear-regression)


## The Problem
Suppose we have some sensitive data we wish to process on a remote server.
The usual approach is to send the data over a secure connection to be processed server-side.

```py
# examples/intro/insecure.py

# The server
def process(x):
    return x**3 - 3*x + 1


# The client
sensitive_data = [-30, -5, 17, 28]
for entry in sensitive_data:
    print(entry, process(entry)) # Bad! We are leaking sensitive information.

```
The result:
```txt
// examples/intro/insecure.out

-30 -26909
-5 -109
17 4863
28 21869

```
However, this requires trusting the server to keep your data confidential. One rogue admin or database hack is all it takes to expose your sensitive data to the public.

## The Solution
A few lines of extra code is all it takes to implement Full Homomorphic Encryption (FHE):
```py
# examples/intro/secure.py

from simplefhe import (
    encrypt, decrypt,
    generate_keypair,
    set_public_key, set_private_key, set_relin_keys,
    display_config
)

# In a real application, the keypair would be generated once,
# and only the public key would be provided to the server.
# A more realistic example is given later.
public_key, private_key, relin_keys = generate_keypair()
set_private_key(private_key)
set_public_key(public_key)
set_relin_keys(relin_keys)
# Don't worry about the relin keys for now.
# They should be shared between the client
# and the server, just like the public keys.

display_config()


# The server
def process(x):
    return x**3 - 3*x + 1


# The client
sensitive_data = [-30, -5, 17, 28]
for entry in sensitive_data:
    encrypted = encrypt(entry) # Encrypt the data...
    result = process(encrypted) # Process the data encrypted on the server...
    print(entry, decrypt(result)) # Decrypt the result on the client.

```
We obtain the same results, as expected:
```txt
// examples/intro/secure.out

===== simplefhe config =====
mode: integer (exact)
min_int: -262143
max_int: 262144
public_key: initialized
private_key: initialized
relin_keys: initialized

-30 -26909
-5 -109
17 4863
28 21869

```
In this example, we encrypt the data on the client, *send only the encrypted data to the server,* process the encrypted data server-side,
and return the encrypted result to be client-side decrypted. This requires zero trust of the remote server.

## A More Realistic Example
Of course, the client and server will generally be separate applications.
Here we demonstrate a more realistic pipeline.

### Step 1: Keypair Generation
We first generate a fixed pair of keys:
```py
# examples/realistic/1_keygen.py

from simplefhe import generate_keypair

public_key, private_key, relin_keys = generate_keypair()
public_key.save('keys/public.key')
private_key.save('keys/private.key')
relin_keys.save('keys/relin.key')
print('Keypair saved to keys/ directory')

```

### Step 2: Client-Side Encryption
Next, we encrypt our sensitive data on the client.
Here we save the encrypted results to disk,
but in the real-world these files would be sent over a network to the server.
```py
# examples/realistic/2_encrypt.py

from simplefhe import encrypt, load_public_key, load_relin_keys, display_config

load_public_key('keys/public.key')
load_relin_keys('keys/relin.key')
display_config()


# Encrypt our data (client-side)
sensitive_data = [-30, -5, 17, 28]

for i, entry in enumerate(sensitive_data):
    encrypted = encrypt(entry)
    encrypted.save(f'inputs/{i}.dat')
    print(f'[CLIENT] Input {entry} encrypted to inputs/{i}.dat')


# We may then safely send these files to the server
# over a (possibly insecure) network connection

```
Output:
```txt
// examples/realistic/2_encrypt.out

===== simplefhe config =====
mode: integer (exact)
min_int: -262143
max_int: 262144
public_key: initialized
private_key: initialized
relin_keys: initialized

[CLIENT] Input -30 encrypted to inputs/0.dat
[CLIENT] Input -5 encrypted to inputs/1.dat
[CLIENT] Input 17 encrypted to inputs/2.dat
[CLIENT] Input 28 encrypted to inputs/3.dat

```

### Step 3: Server-Side Processing
We process the encrypted data from the client.
The server never has access to the private key,
and can never decrypt the client's sensitive data.
```py
# examples/realistic/3_process.py

from simplefhe import load_public_key, load_relin_keys, display_config, load_encrypted_value


# The private key never leaves the client.
load_public_key('keys/public.key')
load_relin_keys('keys/relin.key')
display_config()

# Process values on server.
def f(x): return x**3 - 3*x + 1

for i in range(4):
    # Load encrypted value sent from client
    value = load_encrypted_value(f'inputs/{i}.dat')

    # simplefhe seamlessly translates all arithmetic to
    # FHE encrypted operations.
    # We never gain access to the unencrypted information.
    result = f(value) 

    # Send encrypted result back to client
    result.save(f'outputs/{i}.dat')
    print(f'[SERVER] Processed entry {i}: inputs/{i}.dat -> outputs/{i}.dat')


```
Output:
```txt
// examples/realistic/3_process.out

===== simplefhe config =====
mode: integer (exact)
min_int: -262143
max_int: 262144
public_key: initialized
private_key: initialized
relin_keys: initialized

[SERVER] Processed entry 0: inputs/0.dat -> outputs/0.dat
[SERVER] Processed entry 1: inputs/1.dat -> outputs/1.dat
[SERVER] Processed entry 2: inputs/2.dat -> outputs/2.dat
[SERVER] Processed entry 3: inputs/3.dat -> outputs/3.dat

```

### Step 4: Client-Side Decryption
Finally, the encrypted results are sent back to the client,
where they are decrypted.
The private key never needs to leave the client.
```py
# examples/realistic/4_decrypt.py

from simplefhe import (
    load_private_key, load_relin_keys,
    display_config,
    decrypt, load_encrypted_value
)

# Note: this is the only step at which the private key is used!
load_private_key('keys/private.key')
load_relin_keys('keys/relin.key')
display_config()


# Decrypt results from the server (client-side)
sensitive_data = [-30, -5, 17, 28]

for i, entry in enumerate(sensitive_data):
    encrypted = load_encrypted_value(f'outputs/{i}.dat')
    result = decrypt(encrypted)
    print(f'[CLIENT] Result for {entry}: {result}')

```
As expected, we obtain the correct results:
```txt
// examples/realistic/4_decrypt.out

===== simplefhe config =====
mode: integer (exact)
min_int: -262143
max_int: 262144
public_key: missing
private_key: missing
relin_keys: missing

[CLIENT] Result for -30: -26909
[CLIENT] Result for -5: -109
[CLIENT] Result for 17: 4863
[CLIENT] Result for 28: 21869

```

## Installation
`simplefhe` depends on [SEAL-Python](https://github.com/Huelse/SEAL-Python) and all its prerequisites.
After installing `SEAL-Python`, the `simplefhe` library
is just a `pip` install away:
`pip3 install simplefhe`

## Notes
- To enable floating point computations (results will be approximate):
```py
from simplefhe import initialize
initialize('float')
```
This must be done before any other `simplefhe` code (keygen, encryption/decryption, etc.) is executed.
A full example is shown later.
- To increase the maximum range of allowable integers:
```py
from simplefhe import initialize

MAX_INT = pow(2, 25)
initialize('int', max_int=MAX_INT)
```
Integers in the range `[-MAX_INT + 1, MAX_INT]` inclusive are representable.
- Comparison operations (`<`, `=`, `>`) are not supported on encrypted data.
If they were, it would be pretty easy to figure out what the plaintext is!
As a side effect, it's not really possible to branch based on encrypted data.
- There is some randomness in the encryption process: the same value, encrypted with the same key, will yield different ciphertexts.
This prevents a simple plaintext enumeration attack.

## Floating Point
The following code shows a full floating point demo:
```py
# examples/float_demo.py

from simplefhe import (
    encrypt, decrypt,
    generate_keypair,
    set_public_key, set_private_key, set_relin_keys,
    initialize, display_config
)

initialize('float')

public_key, private_key, relin_key = generate_keypair()
set_private_key(private_key)
set_public_key(public_key)
set_relin_keys(relin_key)

display_config()


# The server
def process(x):
    return x**3 - 3.1*x + 5.3


# The client
sensitive_data = [-3.2, 0.1, 5.3, 50.6]
for entry in sensitive_data:
    insecure_result = process(entry)
    secure_result = decrypt(process(encrypt(entry)))
    print(
        f'{entry:8.1f}',
        '|',
        f'{insecure_result:12.2f}',
        f'{secure_result:12.2f}'
    )

```
The results are approximate, and will change slightly on each run:
```txt
// examples/float_demo.out

===== simplefhe config =====
mode: float (approximate)
public_key: initialized
private_key: initialized
relin_keys: initialized

    -3.2 |       -17.55       -17.55
     0.1 |         4.99         4.99
     5.3 |       137.75       137.75
    50.6 |    129402.66    129402.76

```

## Linear Regression
See [here](https://github.com/wgxli/simple-fhe/examples/linear-regression/) for a working server-side linear regression example.
