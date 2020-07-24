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
