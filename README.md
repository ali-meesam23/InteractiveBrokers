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
P.S. make sure that the '_vars.py' file exists in the same folder as all the other files.
___

## **_Contract.py**
**Creating a Ticker ID CSV file**

Ticker id's are accurately creating a contract for a specific instrument. In order to speed up and make less frequent calls, I have created a CSV file to make sure that the ticker ID are stored and if the ID doesn't exist, the new call to IB is made and the ID along with its ticker is stored in a 'IB_Ticker_Ids.csv' file

Store Ticker_ID Path in a variable on ~/.bash_profile or ~/.zshrc

```
sudo nano ~/.zshrc
OR
sudo nano ~/.bash_profile

export IB_TICKERID_PATH="$HOME/<FOLDER PATH>/IB_Ticker_Ids.csv"
```
Make sure to create an empty CSV file in the location
```
touch $HOME/<FOLDER PATH>/IB_Ticker_Ids.csv
```
___
## **_News.py**
To archive new headlines, create a environment variable similar to 'IB_TICKERID_PATH'.
```
export STOCK_DATA_PATH="$HOME/<STOCK DATA DIR>/"
```
Create a directory called News_ib in STOCK_DATA_PATH
```
mkdir $STOCK_DATA_PATH/News_ib
```
___
## **_OHLC_HistoricalData.py**
For this file to propely execute and archive OHLC data, make sure to have STOCK_DATA_PATH stored in the environment variable

