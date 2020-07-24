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

