from pathlib import Path
from simplefhe import initialize, generate_keypair

# All subsequent processing must be done with the same initialization
initialize('float')

# Generate keypair
public_key, private_key, relin_keys = generate_keypair()

# Save keys
Path('keys').mkdir(exist_ok=True)
public_key.save('keys/public.key')
private_key.save('keys/private.key')
relin_keys.save('keys/relin.key')

print('Keys saved to keys/ directory')
