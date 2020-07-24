# The server
def process(x):
    return x**3 - 3*x + 1


# The client
sensitive_data = [-30, -5, 17, 28]
for entry in sensitive_data:
    print(entry, process(entry)) # Bad! We are leaking sensitive information.
