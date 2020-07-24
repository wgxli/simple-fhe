from simplefhe import (
    encrypt, decrypt,
    generate_keypair,
    set_public_key, set_private_key, set_relin_keys,
    initialize, display_config
)

initialize('float')

public_key, private_key, relin_key = generate_keypair()
set_private_key(private_key)
set_public_key(public_key)
set_relin_keys(relin_key)

display_config()


# The server
def process(x):
    return x**3 - 3.1*x + 5.3


# The client
sensitive_data = [-3.2, 0.1, 5.3, 50.6]
for entry in sensitive_data:
    insecure_result = process(entry)
    secure_result = decrypt(process(encrypt(entry)))
    print(
        f'{entry:8.1f}',
        '|',
        f'{insecure_result:12.2f}',
        f'{secure_result:12.2f}'
    )
