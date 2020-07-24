from simplefhe import (
    encrypt, decrypt,
    generate_keypair,
    set_public_key, set_private_key, set_relin_keys,
    initialize, display_config
)

initialize('int')

public_key, private_key, relin_key = generate_keypair()
set_private_key(private_key)
set_public_key(public_key)
set_relin_keys(relin_key)

display_config()


# The server
def process(x):
    return x**21


# The client
sensitive_data = [-3, 1, 3, 10]
for entry in sensitive_data:
    insecure_result = process(entry)
    secure_result = decrypt(process(encrypt(entry)))
    print(
        entry,
        insecure_result,
        secure_result
    )
