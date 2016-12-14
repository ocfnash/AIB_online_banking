import requests, json, hashlib, urllib, binascii, base64, uuid, Crypto.Random, Crypto.Cipher.AES as AES

base_url = 'https://onlinebankingservices.aib.ie/inet/roi/api/'
deviceId = str(uuid.uuid4())
regNumber, pacDigits = raw_input('Please enter your 8-digit registration number and 5-digit PAC number separated by space: ').split()

def DHParametersFromGenerateResponseBody(body):
    data = json.loads(body)['data']
    p, g, by = map(int, (data['p'], data['g'], data['y']))
    ax = 2 # Our chosen Diffie-Hellman "secret" key.
    return (p, g, by, ax, g**ax % p)

def derivedKeyFromPassphraseAndSalt(passPhrase, cipherSalt):
    return hashlib.pbkdf2_hmac('sha1', passPhrase, cipherSalt, 1000, 16)

def derivedKeyFromDHKeys(ax, by, p):
    hexEncodedDHSecret = format(by**ax % p, 'x')
    passPhrase = binascii.hexlify(hashlib.md5(deviceId + hexEncodedDHSecret + deviceId).digest())
    cipherSalt = passPhrase[:16]
    return derivedKeyFromPassphraseAndSalt(passPhrase, cipherSalt)

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

def keysAndDataFromDecryptedResponse(derivedKey, response_dict):
    if 'passPhrase' in response_dict and 'cipherSalt' in response_dict:
        derivedKey = derivedKeyFromPassphraseAndSalt(str(response_dict['passPhrase']), str(response_dict['cipherSalt']))
    transactionKey = response_dict['transactionKey'] if 'transactionKey' in response_dict else None
    return (derivedKey, transactionKey, response_dict['data'])

def postEncryptedRequest(derivedKey, transactionKey, url_suffix, params):
    params.append(('deviceId', deviceId))
    if transactionKey is not None:
        params.append(('transactionKey', transactionKey))
    r = requests.post(base_url + url_suffix, data=encryptRequestBody(derivedKey, urllib.urlencode(params)))
    return keysAndDataFromDecryptedResponse(derivedKey, decryptResponseBody(derivedKey, r.content))

r = requests.post(base_url + 'handshake/generate.htm', data=[('deviceId', deviceId), ('mode', 'y')])
p, g, by, ax, ay = DHParametersFromGenerateResponseBody(r.content)
derivedKey = derivedKeyFromDHKeys(ax, by, p)
transactionKey = None

requests.post(base_url + 'handshake/verify.htm', data=[('deviceId', deviceId), ('y', ay)])

params = [('regNumber', regNumber)]
derivedKey, transactionKey, response_data = postEncryptedRequest(derivedKey, transactionKey, 'user/login.htm', params)
pacIdxs = map(lambda x: int(x)-1, (response_data['pacPosition1'], response_data['pacPosition2'], response_data['pacPosition3']))

params = [('pacDigit1', pacDigits[pacIdxs[0]]), ('pacDigit2', pacDigits[pacIdxs[1]]), ('pacDigit3', pacDigits[pacIdxs[2]])]
derivedKey, transactionKey, response_data = postEncryptedRequest(derivedKey, transactionKey, 'auth/pacdigits.htm', params)

params = [('accountType', 'nonlife')]
derivedKey, transactionKey, response_data = postEncryptedRequest(derivedKey, transactionKey, 'account/list.htm', params)
for account in response_data:
    print account['displayName'], account['balance']['amount'], account['balance']['fraction'], account['balance']['currency'], account['balance']['indicator']
