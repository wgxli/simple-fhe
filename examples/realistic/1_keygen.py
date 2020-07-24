from simplefhe import generate_keypair

public_key, private_key  = generate_keypair()
public_key.save('keys/public.key')
private_key.save('keys/private.key')
print('Keypair saved to keys/ directory')
