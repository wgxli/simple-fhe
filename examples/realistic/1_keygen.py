from pathlib import Path
from simplefhe import generate_keypair

public_key, private_key, relin_keys = generate_keypair()

Path('keys').mkdir(exist_ok=True)
public_key.save('keys/public.key')
private_key.save('keys/private.key')
relin_keys.save('keys/relin.key')

print('Keypair saved to keys/ directory')
