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
