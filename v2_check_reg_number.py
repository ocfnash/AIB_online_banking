import requests, json, hashlib, urllib, binascii, base64, uuid, Crypto.Random, Crypto.Cipher.AES as AES

base_url = 'https://onlinebankingservices.aib.ie/inet/roi/api/'
deviceId = str(uuid.uuid4())
regNumber = raw_input('Please enter your 8-digit registration number: ')

def DHParametersFromGenerateResponseBody(body):
    data = json.loads(r.content)['data']
    p, g, by = map(int, (data['p'], data['g'], data['y']))
    ax = 2 # Our chosen Diffie-Hellman "secret" key.
    return (p, g, by, ax, g**ax % p)

def derivedKeyFromDHKeys(ax, by, p):
    hexEncodedDHSecret = format(by**ax % p, 'x')
    passPhrase = binascii.hexlify(hashlib.md5(deviceId + hexEncodedDHSecret + deviceId).digest())
    cipherSalt = passPhrase[:16]
    return hashlib.pbkdf2_hmac('sha1', passPhrase, cipherSalt, 1000, 16)

def PKCS7Pad(s, block_size = 16):
    n = block_size - len(s) % block_size
    return s + n * chr(n)

def PKCS7Unpad(s):
    return s[:-ord(s[-1])]

def encryptRequestBody(derivedKey, body):
    iv = Crypto.Random.new().read(AES.block_size)
    cipher = AES.new(derivedKey, AES.MODE_CBC, iv)
    encryptedBody = cipher.encrypt(PKCS7Pad(body))
    return [('param1', deviceId),
            ('param2', base64.b64encode(encryptedBody)),
            ('param3', base64.b64encode(iv))]

def decryptResponseBody(derivedKey, body):
    body_dict = json.loads(body)
    iv = base64.b64decode(body_dict['data2'])
    cipher = AES.new(derivedKey, AES.MODE_CBC, iv)
    decryptedBody = PKCS7Unpad(cipher.decrypt(base64.b64decode(body_dict['data1'])))
    return json.loads(decryptedBody)

r = requests.post(base_url + 'handshake/generate.htm', data=[('deviceId', deviceId), ('mode', 'y')])
p, g, by, ax, ay = DHParametersFromGenerateResponseBody(r.content)
derivedKey = derivedKeyFromDHKeys(ax, by, p)

requests.post(base_url + 'handshake/verify.htm', data=[('deviceId', deviceId), ('y', ay)])

r = requests.post(base_url + 'user/login.htm', data=encryptRequestBody(derivedKey, urllib.urlencode([('deviceId', deviceId), ('regNumber', regNumber)])))
response_dict = decryptResponseBody(derivedKey, r.content)
print response_dict['data']['name'], 'last logged in', response_dict['data']['lastLogin']
