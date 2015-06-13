Visit
[this page](http://www.olivernash.org/2015/06/14/security-theatre-at-allied-irish-banks/index.html)
for more detail.

Allied Irish Banks have
[web](https://onlinebanking.aib.ie/inet/roi/login.htm) and
[mobile](https://mobilebanking.aib.ie/mob/roi/login.htm) portals
providing the usual sorts of banking
services that we have come to expect our banks to provide online.

Although certain transactions (e.g., transferring funds to a new payee)
thankfully require two-factor authentication, the basic login protocol
(which still grants a lot of power, including limited fund transfer
capabilities) is far, far too insecure.

The insecurity stems from the fact that the 'secret' 8-digit PIN
for a great many accounts (not all accounts, but I estimate several hundreds of
thousands) _is simply the account-holder's birthdate_ followed by two
apparently-random decimal digits (so it looks like DDMMYYNN). Really!

The second of the two login stages requires supplying 3 digits from a second
secret PIN (5-decimal-digits long) but if all that is sought is access to
at least one account then the large number of extant accounts means the goal is
easily attainable.

**A malicious person could even deliberately make three
repeated attempts against each account and require hundreds of thousands of
people to have to visit their branches to have their online accounts
unlocked.** Such an event would completely overwhelm the branch network and
even after the accounts were unlocked, the event could be repeated.

I would be unhappy if my grocery store used this sort security theatre to
'protect' my personal information 
but for a bank this sort of behaviour is seriously dangerous. As might be
expected, **reports of these concerns both to AIB and to the
[Irish Financial Services Ombudsman](https://www.financialombudsman.ie/)
were dismissed with off-the-shelf replies.**

The intention behind the creation of this repo is to illustrate just how easy
it would be for a malicious person to carry out actions such as those above.
For this reason, two python scripts are provided. The first is written to be
as simple and barebones as possible emphasising simplicty; the second is
written to send HTTP requests that are indistinguishable from the bank's
own mobile app.

As a bonus, it's actually quite handy to be able to interface with online
banking from the command line. The scripts use python's `raw_input` instead of
`sys.argv` because it is not safe to have banking PINs in shell history.

Note that you might need to:
```bash
% pip install requests bs4
```

Finally, python aside, here is a redacted history of a log-in
using just three simple `curl` invocations:
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
