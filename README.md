# InteractiveBrokers
Python APIs to connect to TWS and IBGateway. Ideal for building day trading bots and pulling market data.

Make sure to install the latest version of ibapi use the following link and follow the instructions:
<a>https://interactivebrokers.github.io/#</a>

(I used TWS API stable)

There are better ways of storing static variables (account info, ip addresses and hostname, etc.) I have used a .py file called _vars.py to store the following variables:
* ACCOUNT_NUMBER
* ACCOUNT_NAME
* ACCOUNT_TYPE
* SOFTWARE
* HOST
* CLIENT_ID

e.g. ACCOUNT_NUMBER="DU1214314" (use proper python3 syntax)
____
P.S. make sure the file exists in the same folder as all the other files.

