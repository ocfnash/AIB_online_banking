Allied Irish Banks have
[web](https://onlinebanking.aib.ie/inet/roi/login.htm) and mobile portals providing the usual sorts of services that we have come to expect our banks to provide online.

For the newer mobile API, the bank has gone to some trouble to obfuscate it, using a custom Diffie-Hellman implementation. The scripts in this repository give details on how to deal with this.

I created this repository to highlight AIB's online security problems when I wrote about them [here](http://www.olivernash.org/2015/06/14/security-theatre-at-allied-irish-banks/index.html) and [here](http://olivernash.org/2015/11/18/security-theatre-at-allied-irish-banks-act-2/index.html). The good news is that some time in early-to-mid 2016, the bank closed the loophole highlighted in the second of these posts.

The scripts here should enable anyone to write their own front end for the bank's API.
