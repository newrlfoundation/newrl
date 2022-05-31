import hashlib


wallet_address = input('Enter wallet address: ')
hs = hashlib.blake2b(digest_size=20)
hs.update(wallet_address.encode())
person_id = 'pi' + hs.hexdigest()
print(person_id)