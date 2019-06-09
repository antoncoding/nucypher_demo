import umbral
from umbral import pre, keys, signing

umbral.config.set_default_curve()

# Generate Umbral keys for Alice.
alices_private_key = keys.UmbralPrivateKey.gen_key()
alices_public_key = alices_private_key.get_pubkey()
print('Alice Pubkey: \t {}'.format(alices_public_key))

alices_signing_key = keys.UmbralPrivateKey.gen_key()
alices_verifying_key = alices_signing_key.get_pubkey()
print('Alice Verifying Key:\t{}'.format(alices_verifying_key))

alices_signer = signing.Signer(private_key=alices_signing_key)


# Generate Umbral keys for Bob.
bobs_private_key = keys.UmbralPrivateKey.gen_key()
bobs_public_key = bobs_private_key.get_pubkey()
print('Bob Pubkey: \t {}'.format(bobs_public_key))


# Old PKE Logic
# Encrypt data with Alice's public key.
plaintext = b'Anton and Nucypher Re-Encryption is Cool!'
ciphertext, capsule = pre.encrypt(alices_public_key, plaintext)

# Decrypt data with Alice's private key.
cleartext = pre.decrypt(ciphertext=ciphertext,
                        capsule=capsule,
                        decrypting_key=alices_private_key)

assert plaintext==cleartext, 'PKE Failed.'


# Alice generates "M of N" re-encryption key fragments (or "KFrags") for Bob.
# In this example, 10 out of 20.
kfrags = pre.generate_kfrags(delegating_privkey=alices_private_key, signer=alices_signer, receiving_pubkey=bobs_public_key,
        threshold=10, N=20)



# Several Ursulas perform re-encryption, and Bob collects the resulting `cfrags`.
# He must gather at least `threshold` `cfrags` in order to activate the capsule.

capsule.set_correctness_keys(delegating=alices_public_key, receiving=bobs_public_key, verifying=alices_verifying_key)

cfrags = list()           # Bob's cfrag collection
for kfrag in kfrags[:10]:
    cfrag = pre.reencrypt(kfrag=kfrag, capsule=capsule)
    cfrags.append(cfrag)    # Bob collects a cfrag

# Bob activates and opens the capsule
for cfrag in cfrags:
  capsule.attach_cfrag(cfrag)

bob_cleartext = pre.decrypt(ciphertext=ciphertext,
                            capsule=capsule,
                            decrypting_key=bobs_private_key)

assert bob_cleartext == plaintext