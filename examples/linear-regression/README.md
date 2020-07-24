# Linear Regression Example
This is a quick demo of multivariate linear regression
on encrypted client data.
For our example, we fit a linear function from 3D inputs to 1D outputs,
using 50 encrypted datapoints.
Partial results are returned to the client, who needs to perform relatively few computations to obtain the final regression coefficients.

The overhead of FHE only makes sense for large quantities of data, stored server-side; for example, the client may continuously stream
encrypted datapoints to the server, which computes a regression on large quantities of data accumulated over time.

## Step 1: Keypair Generation
We generate an store a set of keys to be used throughout the process.
```py
# 1_keygen.py

from simplefhe import initialize, generate_keypair

# All subsequent processing must be done with the same initialization
initialize('float')

# Generate keypair
public_key, private_key, relin_keys = generate_keypair()

# Save keys
public_key.save('keys/public.key')
private_key.save('keys/private.key')
relin_keys.save('keys/relin.key')

print('Keys saved to keys/ directory')

```

## Step 2: Client-Side Data Encryption
We generate sample datapoints using a linear model,
and save the encrypted data to disk.
In the real world, the encrypted data would be sent
to the server over a (possibly insecure) network.
```py
# 2_generate.py

# Client-side script to generate data and save in in encrypted format.
import numpy as np

from simplefhe import initialize, encrypt, load_public_key, load_relin_keys


# Initialization and keys
initialize('float')
load_public_key('keys/public.key')
load_relin_keys('keys/relin.key')


# We generate example datapoints according to a linear model:
# y = 3.2 x1 - 1.7 x2 + 0.8 x3 + noise
COEFFICIENTS = np.array([3.2, -1.7, 0.8])
def generate_point():
    xs = np.random.normal(size=3, scale=10)
    noise = np.random.normal(scale=0.2)
    y = np.inner(xs, COEFFICIENTS) + noise
    return (xs, y)


# Generate and save encrypted datapoints
N_DATAPOINTS = 50
for i in range(N_DATAPOINTS):
    print(f'Generating datapoint {i+1} of {N_DATAPOINTS}')
    xs, y = generate_point()

    encrypt(y).save(f'inputs/y-{i}.dat')
    for j, x in enumerate(xs):
        encrypt(x).save(f'inputs/x{j}-{i}.dat')

```

## Step 3: Server-Side Processing
We compute a linear regression over the client's encrypted data.
Since float division is not possible, we compute and send partial results.
The client will need to do some, but not much, post-processing.
```py
# 3_process.py

# Server-side script to perform linear regression on the given data.
from simplefhe import initialize, load_public_key, load_relin_keys, load_encrypted_value

##### Initialization and keys ####
initialize('float')
load_public_key('keys/public.key')
load_relin_keys('keys/relin.key')


#### Online linear regression class ####
class LinearRegression:
    def __init__(self, dimension):
        """
        Initialize an empty linear regression.

        :param dimension: The dimensionality of the independent variable.
        """
        self.XtX = [[0] * dimension for i in range(dimension)]
        self.XtY = [0] * dimension
        self.dimension = dimension

    def update(self, xs, y):
        """Update the model with a new datapoint."""
        for i in range(self.dimension):
            self.XtY[i] += xs[i] * y
            for j in range(self.dimension):
                self.XtX[i][j] += xs[i] * xs[j]

    def dump(self) -> dict:
        """Export the regression coefficients."""
        output = {}
        for i in range(self.dimension):
            output[f'XtY-{i}'] = self.XtY[i]
            for j in range(self.dimension):
                output[f'XtX-{i}-{j}'] = self.XtX[i][j]
        return output


#### Process the client's encrypted data ####
regression = LinearRegression(3)
N_DATAPOINTS = 50
for i in range(N_DATAPOINTS):
    # Load the ith datapoint
    xs = []
    y = load_encrypted_value(f'inputs/y-{i}.dat')
    for j in range(3):
        xs.append(load_encrypted_value(f'inputs/x{j}-{i}.dat'))

    # Update regression
    regression.update(xs, y)
    print(f'Procesed datapoint {i+1} of {N_DATAPOINTS}')

# Dump regression coefficients
coefficients = regression.dump()
for name, value in coefficients.items():
    value.save(f'outputs/{name}.dat')

```

## Step 4: Client-Side Decryption
The client decrypts and post-processes the final results.
```py
# 4_decrypt.py

# Client-side script to decrypt the server's results
import numpy as np

from simplefhe import (
    initialize,
    decrypt, load_encrypted_value,
    load_private_key, load_relin_keys
)


# Initialization and keys
initialize('float')
load_private_key('keys/private.key')
load_relin_keys('keys/relin.key')


# Decrypt server's results
XtX = np.zeros(shape=[3, 3])
XtY = np.zeros(shape=3)
for i in range(3):
    XtY[i] = decrypt(load_encrypted_value(f'outputs/XtY-{i}.dat'))
    for j in range(3):
        XtX[i, j] = decrypt(load_encrypted_value(f'outputs/XtX-{i}-{j}.dat'))

# Some post-processing
coefficients = np.linalg.inv(XtX) @ XtY

# Display results
GROUND_TRUTH = [3.2, -1.7, 0.8]
for i, pair in enumerate(zip(GROUND_TRUTH, coefficients)):
    a, b = pair
    print(f'Coefficient {i}: Expected {a:.4f}, Received {b:.4f}')

```
```txt
// 4_decrypt.out

Coefficient 0: Expected 3.2000, Received 3.1986
Coefficient 1: Expected -1.7000, Received -1.6964
Coefficient 2: Expected 0.8000, Received 0.8015

```
