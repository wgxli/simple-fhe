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
