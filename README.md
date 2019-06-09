
# Nucypher CLI Charactor Demo
* This is a demo code following official tutorial from https://www.youtube.com/watch?v=om0tew-Z4gE.
* Some changes are made to fit the new version. (0.1.0-alpha2.2)

## Installation
```
pip3 install nucypher
```
Or follow the installation guid on https://docs.nucypher.com/en/latest/guides/installation_guide.html


```python
from base64 import b64decode, b64encode
import json
import requests
import maya # to build ISO format string
import datetime
```

## Run Ursula
```
nucypher ursula run --dev --federated-only
```

## Run Alice Node
```shell
nucypher alice run --dev --federated-only --teacher-uri localhost:10151
```
Paste the `Alice Verifying Key` in the following


```python
alice = "http://127.0.0.1:8151"
alice_verifying_key = '02b7cd69017a5ce728074ac995793c0ac24b53fc22e0a552c3ed5d72b86274df3b'

```

###  Get Policy Encrypting Key


```python
label = 'villa'
derivation_response = requests.post("{}/derive_policy_encrypting_key/{}".format(alice, label))
villa_key = json.loads(derivation_response.text)['result']['policy_encrypting_key']
print('Policy {}\tEncryption key:\t{}'.format(label, villa_key))

```

    Policy villa	Encryption key:	030a04a0754265051833bdd1beaacfc153068100b5050581d70d0de979aba38daf


## Start Enrico Node
Start Nucypher Enrico with the Policy Encryption Key.
```
ucypher enrico run --policy-encrypting-key 030a04a0754265051833bdd1beaacfc153068100b5050581d70d0de979aba38daf --http-port 5151
```


```python
enrico = 'http://127.0.0.1:5151'
```


```python
my_message = b"I love you! Let's Try out this Nucypher" # It should be bytes
encryption_request = { "message": b64encode(my_message).decode()}
encryption_respone = requests.post("{}/encrypt_message".format(enrico), data=json.dumps(encryption_request))
encrypted_message = json.loads(encryption_respone.text)['result']
encrypted_message
```




    {'message_kit': 'A3RCisAfCRdDQtCPVuHCi5/PzR4yYkrrAOqZdV8tLTLlAge+mtr2aIsSPqVYTz5mQUnO508Izy1i9zENB8VmOepJOhgwXN3qg45gTQkYlAXpyWKL9IeA6K9NZoa0OfQ33AID6/jWervG4G4lZlj4tx+VdzqREVRLvdsV7I87bAmtR8Mm8s081TYl+NwfD9/ayyl8menu4V3VqzKvpYezCsuxnw2Q00KQMMyBaCVeyZtqhD3IZGDpagQx7wBSdokUp3GWAgGn5BYIT5vfMUrmjoyxIxThb4KTnn5Cwv/HBJjY7E0AbExCJXolo10NoyIns4zLElxnuFTRmRrAwTma4n2d9G+S8807RDOgwQ66rVybwTHl5D4SEYnAKA==',
     'signature': '2CxNeR9PD1B0bZvcc0ogy8vk0L09DDqrrzkKhWMCzGDT0p67AWT1AbCz4Hm0oR32/7GukG7maAKgmZaCROc+HQ=='}



## Start Bob 

```
nucypher bob run --dev --federated-only --teacher-uri localhost:10151 --http-port 11151
```

Start Node Bob and past `bob_verifying_key` and `bob_encrypting_key` here.


```python
bob = 'http://127.0.0.1:11151'
bob_verifying_key = '024ce49fb4d7c96cbcad50e716b340054e3219a4b953f6b707736f8e405c8e6bf9'
bob_encrypting_key = '03736e6fcc0f58c9df38c8009a7cd1bd9635ce75040f9a6860e784b8573f061da0'

```

### Bob: Try Retrieve the Message before Alice Grant Access


```python
retrieval = {}
retrieval['label'] = label
retrieval['policy_encrypting_key'] = villa_key
retrieval['alice_verifying_key'] = alice_verifying_key
retrieval['message_kit'] = encrypted_message['message_kit']

retrieval_response = requests.post('{}/retrieve'.format(bob), json=retrieval)
retrieval_response

```




    <Response [500]>



### Alice: Grant Access (of label Villa) to Bob


```python
expiration = (maya.now() + datetime.timedelta(days=3)).iso8601()
print(expiration)
# Grant Access to bob
grant = {}
grant['bob_verifying_key'] = bob_verifying_key # not on API Doc
grant['bob_encrypting_key'] = bob_encrypting_key
grant['expiration'] = expiration
grant['label'] = label
grant['m'] = 1
grant['n'] = 1
res = requests.put('{}/grant'.format(alice), json=grant)
print('Grant Access Call:\t{}'.format(res.status_code))
grant_res = json.loads(res.text)['result']
```

    2019-06-12T09:49:53.144843Z
    Grant Access Call:	200


### Bob: Retrieve Data Again


```python
retrieval_response = requests.post('{}/retrieve'.format(bob), json=retrieval)
print(retrieval_response)
```

    <Response [200]>



```python
encoded_text = json.loads(retrieval_response.text)['result']['cleartexts']
print('Decrypted Message = {}'.format(b64decode(encoded_text[0])))
```

    Decrypted Message = b"I love you! Let's Try out this Nucypher"


### Yay!
We successfully Got the message from Bob's side!
