# A Simple Drop-In Solution for Full Homomorphic Encryption
Full Homomorphic Encryption (FHE) allows untrusted (e.g. cloud) applications
to operate directly on encrypted data, eliminating the need for server-side decryption or trust.

`simplefhe` is a Python library for FHE that intends to be as easy-to-use as possible.
In the simplest case, just a few lines of code are all you need to have working FHE!

## The Problem
Suppose we have some sensitive data we wish to process on a remote server.
The usual approach is to send the data over a secure connection to be processed server-side.

```python
# The server
def process(x):
    return x*x - 3*x + 1


# The client
sensitive_data = [-30, -5, 17, 28]
for entry in sensitive_data:
    print(entry, process(entry)) # Bad! We are leaking sensitive information.
```
The result:
```
-30 991
-5 41
17 239
28 701
```
However, this requires trusting the server to keep your data confidential. One rogue admin or database hack is all it takes to expose your sensitive data to the public.

## The Solution
A few lines of extra code is all it takes to implement Full Homomorphic Encryption (FHE):
```python
from simplefhe import (
    encrypt, decrypt,
    generate_keypair,
    set_public_key, set_private_key,
    display_config
)

# In a real application, the keypair would be generated once,
# and only the public key would be provided to the server.
# A more realistic example is given later.
public_key, private_key = generate_keypair()
set_private_key(private_key)
set_public_key(public_key)

display_config()


# The server
def process(x):
    return x*x - 3*x + 1


# The client
sensitive_data = [-30, -5, 17, 28]
for entry in sensitive_data:
    encrypted = encrypt(entry) # Encrypt the data...
    result = process(encrypted) # Process the data encrypted on the server...
    print(entry, decrypt(result)) # Decrypt the result on the client.
```
We obtain the same results, as expected:
```
===== simplefhe config =====
mode: integer (exact)
min_int: -1048575
max_int: 1048576
public_key: initialized
private_key: initialized

-30 991
-5 41
17 239
28 701
```
In this example, we encrypt the data on the client, *send only the encrypted data to the server,* process the encrypted data server-side,
and return the encrypted result to be client-side decrypted. This requires zero trust of the remote server.

## A More Realistic Example
Of course, the client and server will generally be separate applications.
Here we demonstrate a more realistic pipeline.

### Step 1: Keypair Generation
We first generate a fixed pair of keys:
```python
from simplefhe import generate_keypair

public_key, private_key  = generate_keypair()
public_key.save('keys/public.key')
private_key.save('keys/private.key')
print('Keypair saved to keys/ directory')
```

### Step 2: Client-Side Encryption
Next, we encrypt our sensitive data on the client.
Here we save the encrypted results to disk,
but in the real-world these files would be sent over a network to the server.
```python
from simplefhe import encrypt, load_public_key, display_config

load_public_key('keys/public.key')
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
```
===== simplefhe config =====
mode: integer (exact)
min_int: -1048575
max_int: 1048576
public_key: initialized
private_key: missing

[CLIENT] Input -30 encrypted to inputs/0.dat
[CLIENT] Input -5 encrypted to inputs/1.dat
[CLIENT] Input 17 encrypted to inputs/2.dat
[CLIENT] Input 28 encrypted to inputs/3.dat
```

### Step 3: Server-Side Processing
We process the encrypted data from the client.
The server never has access to the private key,
and can never decrypt the client's sensitive data.
```python
from simplefhe import load_public_key, display_config, load_encrypted_value

load_public_key('keys/public.key')
display_config()

# Process values on server.
def f(x): return x*x - 3*x + 1

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
```
===== simplefhe config =====
mode: integer (exact)
min_int: -1048575
max_int: 1048576
public_key: initialized
private_key: missing

[SERVER] Processed entry 0: inputs/0.dat -> outputs/0.dat
[SERVER] Processed entry 1: inputs/1.dat -> outputs/1.dat
[SERVER] Processed entry 2: inputs/2.dat -> outputs/2.dat
[SERVER] Processed entry 3: inputs/3.dat -> outputs/3.dat
```

### Step 4: Client-Side Decryption
Finally, the encrypted results are sent back to the client,
where they are decrypted.
The private key never needs to leave the client.
```python
from simplefhe import (
    load_private_key, display_config,
    decrypt, load_encrypted_value
)

# Note: this is the only step at which the private key is used!
load_private_key('keys/private.key')
display_config()


# Decrypt results from the server (client-side)
sensitive_data = [-30, -5, 17, 28]

for i, entry in enumerate(sensitive_data):
    encrypted = load_encrypted_value(f'outputs/{i}.dat')
    result = decrypt(encrypted)
    print(f'[CLIENT] Result for {entry}: {result}')
```
As expected, we obtain the correct results:
```
===== simplefhe config =====
mode: integer (exact)
min_int: -1048575
max_int: 1048576
public_key: missing
private_key: initialized

[CLIENT] Result for -30: 991
[CLIENT] Result for -5: 41
[CLIENT] Result for 17: 239
[CLIENT] Result for 28: 701
```

## Installation
`simplefhe` depends on [SEAL-Python](https://github.com/Huelse/SEAL-Python) and all its prerequisites.
After installing `SEAL-Python`, the `simplefhe` library
is just a `pip` install away:
`pip3 install simplefhe`

## Notes
- To enable floating point computations (results will be approximate):
```python
from simplefhe import initialize
initialize('float')
```
This must be done before any other `simplefhe` code (keygen, encryption/decryption, etc.) is executed.
A full example is shown later.
- Comparison operations (`<`, `=`, `>`) are not supported on encrypted data.
If they were, it would be pretty easy to figure out what the plaintext is!
As a side effect, it's not really possible to branch based on encrypted data.
- There is some randomness in the encryption process: the same value, encrypted with the same key, will yield different ciphertexts.
This prevents a simple plaintext enumeration attack.

## Floating Point
The following code shows a full floating point demo:
```python
from simplefhe import (
    encrypt, decrypt,
    generate_keypair,
    set_public_key, set_private_key, set_relin_key,
    initialize, display_config
)

initialize('float')

public_key, private_key, relin_key = generate_keypair()
set_private_key(private_key)
set_public_key(public_key)
set_relin_key(relin_key)

display_config()


# The server
def process(x):
    return x*x - 3.1*x + 5.3


# The client
sensitive_data = [-3.2, 0.1, 5.3, 12345.6]
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
```
===== simplefhe config =====
mode: float (approximate)
public_key: initialized
private_key: initialized
relin_keys: initialized

    -3.2 |        25.46        25.46
     0.1 |         5.00         5.00
     5.3 |        16.96        16.96
 12345.6 | 152375573.30 152375593.74
```
