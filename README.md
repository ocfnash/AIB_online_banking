Allied Irish Banks have
[web](https://onlinebanking.aib.ie/inet/roi/login.htm) and mobile portals ([v1](https://mobilebanking.aib.ie/mob/roi/login.htm), [v2](https://onlinebankingservices.aib.ie/inet/roi/api/))
providing the usual sorts of services that we have come to expect our banks to provide online.

Unfortunately their security is far from what it should be, as discussed
[here](http://www.olivernash.org/2015/06/14/security-theatre-at-allied-irish-banks/index.html).

At the time of writing there are two primary sources of insecurity:
 1. For a great many accounts (not all accounts, but I estimate perhaps hundreds of thousands) the "secret" account registration number _is simply the account-holder's birthdate_ followed by two apparently-random decimal digits (so it looks like DDMMYYNN). Really!
 2. Using the [v2 API](https://onlinebankingservices.aib.ie/inet/roi/api/) it is possible to determine whether a potential registration number is valid and, if it is valid, the **name and last log-in time** _without attempting a full log-in_.

The bank refuses to admit their systems are insecure. I believe the best way to deal with security problems like this is for the knowledge to be in the public domain. The Python scripts here demonstrate how easy (unfortunately) it would be for a person of malicious intent to exploit these insecurities.

I also include a redacted history of a log-in (to the [v1 mobile API](https://onlinebankingservices.aib.ie/inet/roi/api/)) using just three simple `curl` invocations:
```bash
# Step 0: send a GET request to obtain values of JSESSIONID, TS01bd6060, transactionToken for use in next request.
% curl -v -O 'https://mobilebanking.aib.ie/mob/roi/login.htm' 2>&1 | grep 'Set-Cookie'
% grep transactionToken login.htm

# Step 1: send a POST request containing the 8-digit secret registration number
# to obtain values for JSESSIONID, TS01bd6060, transactionToken in next request
# as well as which 3 of the 5-digit PAC digits have been requested.
% curl -v -O -X POST 'https://mobilebanking.aib.ie/mob/roi/login.htm' \
  -H 'Cookie: JSESSIONID=<REDACTED>; TS01bd6060=<REDACTED>' \
  -d 'transactionToken=<REDACTED>&jsEnabled=TRUE&regNumber=xxxxxxxx&_target1=true' \
  2>&1 | grep 'Set-Cookie'
% grep transactionToken login.htm
% grep 'Digit ' login.htm # Alternatively: sed -n 's/.*\(Digit [0-9]\):.*/\1/p' login.htm | uniq

# Step 2: send a POST request containing the request 3 PAC digits to finish
# the login and obtain the account information (including balance etc).
% curl -v -O -X POST 'https://mobilebanking.aib.ie/mob/roi/login.htm' \
  -H 'Cookie: JSESSIONID=<REDACTED>; TS01bd6060=<REDACTED>' \
  -d 'transactionToken=<REDACTED>&pacDetails.pacDigit1=x&pacDetails.pacDigit2=x&pacDetails.pacDigit3=x&_finish=true'
```
