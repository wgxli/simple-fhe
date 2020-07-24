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
