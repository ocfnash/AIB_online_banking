import re, requests, bs4

regNumber, pacDigits = raw_input('Please enter your 8-digit registration number and 5-digit PAC number separated by space: ').split()

def transactionToken_from_response_body(soup):
    return soup.find_all(id='transactionToken')[0]['value'] # An epoch timestamp in milliseconds

def POST_1_data_from_response_0_body(soup):
    return [('transactionToken', transactionToken_from_response_body(soup)),
            ('jsEnabled', 'TRUE'),
            ('regNumber', regNumber),
            ('_target1', 'true')]

def POST_2_data_from_response_1_body(soup):
    f = lambda css_class : int(re.match(r'Digit ([0-9]):', soup.find_all('div', {'class' : css_class})[0].get_text().strip()).group(1)) - 1
    return [('transactionToken', transactionToken_from_response_body(soup)),
            ('pacDetails.pacDigit1', pacDigits[f('ui-block-a')]),
            ('pacDetails.pacDigit2', pacDigits[f('ui-block-b')]),
            ('pacDetails.pacDigit3', pacDigits[f('ui-block-c')]),
            ('_finish', 'true')]

def cookie_from_response_headers(set_cookie_headers):
    f = lambda key : re.match(r'.*(%s=[^;]+)' % key, set_cookie_headers).group(1)
    return '; '.join((f('JSESSIONID'), f('TS01bd6060'))) # TS0182448a for web

GET_headers = {
    'Proxy-Connection' : 'keep-alive',
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language' : 'en-us',
    'Accept-Encoding' : 'gzip, deflate',
    'Connection' : 'keep-alive',
    'Host' : 'mobilebanking.aib.ie',
    'User-Agent' : 'AIBIPhone2App'
}

def POST_headers_from_response_cookie_headers(headers):
    h = GET_headers.copy()
    h.update({
        'Origin' : 'https://mobilebanking.aib.ie',
        'Referer' : 'https://mobilebanking.aib.ie/mob/roi/login.htm',
        'Content-Type' : 'application/x-www-form-urlencoded',
        'Content-Length' : '%d', # Actually no need to set: requests overrides.
        'Cookie' : cookie_from_response_headers(headers)
    })
    return h

r = requests.get('https://mobilebanking.aib.ie/mob/roi/login.htm', headers=GET_headers) # Request 0
r = requests.post(r.url, data=POST_1_data_from_response_0_body(bs4.BeautifulSoup(r.content)), headers=POST_headers_from_response_cookie_headers(r.headers['set-cookie'])) # Request 1
r = requests.post(r.url, data=POST_2_data_from_response_1_body(bs4.BeautifulSoup(r.content)), headers=POST_headers_from_response_cookie_headers(r.headers['set-cookie'])) # Request 2

print 'Your balance is a whopping:', bs4.BeautifulSoup(r.content).find_all('p', {'class' : 'hide-funds' })[0].get_text().strip()
