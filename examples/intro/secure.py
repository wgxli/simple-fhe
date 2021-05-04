from simplefhe import (
    encrypt, decrypt,
    generate_keypair,
    set_public_key, set_private_key, set_relin_keys,
    display_config
)

# In a real application, the keypair would be generated once,
# and only the public key would be provided to the server.
# A more realistic example is given later.
display_config()
public_key, private_key, relin_keys = generate_keypair()
set_public_key(public_key)
set_relin_keys(relin_keys)
display_config()

set_private_key(private_key)

display_config()


# The server
def process(x):
    return x**3 - 3*x + 1


# The client
sensitive_data = [-30, -5, 17, 28]
for entry in sensitive_data:
    encrypted = encrypt(entry) # Encrypt the data...
    result = process(encrypted) # Process the encrypted data on the server...
    print(entry, decrypt(result)) # Decrypt the result on the client.
