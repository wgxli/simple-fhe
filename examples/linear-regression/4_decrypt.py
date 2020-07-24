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
