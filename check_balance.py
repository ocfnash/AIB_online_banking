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

r = requests.get('https://mobilebanking.aib.ie/mob/roi/login.htm') # Request 0
r = requests.post(r.url, data=POST_1_data_from_response_0_body(bs4.BeautifulSoup(r.content)), cookies=r.cookies) # Request 1
r = requests.post(r.url, data=POST_2_data_from_response_1_body(bs4.BeautifulSoup(r.content)), cookies=r.cookies) # Request 2

print 'Your balance is a whopping:', bs4.BeautifulSoup(r.content).find_all('p', {'class' : 'hide-funds' })[0].get_text().strip()
