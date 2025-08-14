#4002 for paper, 4001 for live.

from ib_insync import IB, Stock, MarketOrder, LimitOrder, StopOrder
import time
import yfinance as yf


ib = IB()

MoneyToUseInPaper = 1000  # Amount of money to start off with (paper trading gives you 1 million by default, wastful to use all of it)
isLive = False
PaperMoneyStart = 996828.4 # Actual is += 1000 

# Given a ticker symbol, buy the stock at market price
def Buy(ticker):
        
    # 1. Define contract
    contract = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(contract)
    
    max_shares = GetSharesBuyable(GetPriceOfTicker(ticker))

    # 5. Place market order
    if max_shares > 99990:
        
        order = MarketOrder("BUY", max_shares)
        trade = ib.placeOrder(contract, order)
        print(f"Buying {max_shares} shares of {ticker}")
    else:
        print("Not enough funds to buy any shares.")
        return


    # 6. Print immediate submission info
    print("Order was submitted, current status:", trade.orderStatus.status)

    # 7. Wait for it to fill
    ib.sleep(1)
    while trade.isActive():
        ib.waitOnUpdate()

    print("Final status:", trade.orderStatus.status)
    if trade.orderStatus.status == 'Filled':
        print("Filled at average price:", trade.orderStatus.avgFillPrice)

# Given a ticker symbol, sell the stock at market price
def Sell(ticker, short_sell=False):
        
    # 1. Define the contract (example: Apple stock)
    contract = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(contract)  # Ensures contract details are fetched
    
    shares_owned = 3151.0
   
    if short_sell:
        shares_owned = GetSharesBuyable(GetPriceOfTicker(ticker))

    # 3. Sell all if you own any
    if shares_owned > 0:
        order = MarketOrder("SELL", shares_owned)
        trade = ib.placeOrder(contract, order)
        print(f"Selling all {shares_owned} shares of {ticker}")
    else:
        print(f"No shares of {ticker} to sell.")
        return

    # 3. Print immediate submission info
    print("Order was submitted, current status:", trade.orderStatus.status)

    # 4. Wait for it to fill
    ib.sleep(1)
    while trade.isActive():
        ib.waitOnUpdate()

    print("Final status:", trade.orderStatus.status)
    if trade.orderStatus.status == 'Filled':
        print("Filled at average price:", trade.orderStatus.avgFillPrice)

# Given a ticker symbol, buy the stock below the given limit price
def BuyLimit(ticker, limitMult):
        
    # 1. Define the contract (example: Apple stock)
    contract = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(contract)  # Ensures contract details are fetched

    # 2. Create and place a market order for 10 shares
    price = GetPriceOfTicker(ticker) * limitMult
    order = LimitOrder("BUY", GetSharesBuyable(price), price)
    trade = ib.placeOrder(contract, order)

    # 3. Print immediate submission info
    print("Order was submitted, current status:", trade.orderStatus.status)

    # 4. Wait for it to fill
    ib.sleep(1)
    while trade.isActive():
        ib.waitOnUpdate()

    print("Final status:", trade.orderStatus.status)
    if trade.orderStatus.status == 'Filled':
        print("Filled at average price:", trade.orderStatus.avgFillPrice)

# Given a ticker symbol, sell the stock above the given limit price
def SellLimit(ticker, limitMult):
        
    # 1. Define the contract (example: Apple stock)
    contract = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(contract)  # Ensures contract details are fetched

    # 2. Create and place a market order for 10 shares

    shares_owned = GetSharesOwned(ticker)
    if shares_owned > 0:
            order = LimitOrder("SELL", shares_owned, GetPriceOfTicker(ticker) * limitMult)
            trade = ib.placeOrder(contract, order)
            print(f"Limit Selling all {shares_owned} shares of {ticker} at {limitMult - 1:}%")
    else:
        print(f"No shares of {ticker} to sell.")
        return

    # 4. Wait for it to fill
    ib.sleep(1)
    while trade.isActive():
        ib.waitOnUpdate()

    print("Final status:", trade.orderStatus.status)
    if trade.orderStatus.status == 'Filled':
        print("Filled at average price:", trade.orderStatus.avgFillPrice)

# Given a ticker symbol, place a stop order to sell the stock bellow the given stop price
def SellStopOrder(ticker, stopMult):
    # 1. Define the contract (example: Apple stock)
    contract = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(contract)  # Ensures contract details are fetched

    shares_owned = GetSharesOwned(ticker)
    stop_price = round(GetPriceOfTicker(ticker) * stopMult, 2)

    if shares_owned > 0:
        order = StopOrder("SELL", shares_owned, stop_price)
        trade = ib.placeOrder(contract, order)
        print(f"Stop Selling all {shares_owned} shares of {ticker} at {stop_price}")
    else:
        print(f"No shares of {ticker} to sell.")
        return

    # 4. Wait for it to fill
    ib.sleep(1)
    while trade.isActive():
        ib.waitOnUpdate()

    print("Final status:", trade.orderStatus.status)
    if trade.orderStatus.status == 'Filled':
        print("Filled at average price:", trade.orderStatus.avgFillPrice)

# Given a ticker symbol, place a stop order to buy the stock above the given stop price
def BuyStopOrder(ticker, stopMult):
    # 1. Define the contract (example: Apple stock)
    contract = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(contract)  # Ensures contract details are fetched

    price = GetPriceOfTicker(ticker) * stopMult
    max_shares = GetSharesBuyable(price)

    if max_shares > 0:
        order = StopOrder("BUY", max_shares, price)
        trade = ib.placeOrder(contract, order)
        print(f"Stop Buying {max_shares} shares of {ticker} at {price}")
    else:
        print("Not enough funds to buy any shares.")
        return

    # 4. Wait for it to fill
    ib.sleep(1)
    while trade.isActive():
        ib.waitOnUpdate()

    print("Final status:", trade.orderStatus.status)
    if trade.orderStatus.status == 'Filled':
        print("Filled at average price:", trade.orderStatus.avgFillPrice)

def PlaceBuyBracketOrder(ticker, profitMult, lossMult):
    contract = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(contract)
    
    current_price = GetPriceOfTicker(ticker)
    print(f"Current price of {ticker} is {current_price}")

    profit_price = round(current_price * profitMult, 2)
    loss_price   = round(current_price * lossMult, 2)
    qty = GetSharesBuyable(current_price)

    # Get a new orderId for parent
    parentId = ib.client.getReqId()

    # Parent (market buy)
    parent = MarketOrder('BUY', qty)
    parent.orderId = parentId
    parent.transmit = False

    # Take-profit (limit sell)
    takeProfit = LimitOrder('SELL', qty, profit_price)
    takeProfit.parentId = parentId
    takeProfit.transmit = False

    # Stop-loss (stop sell)
    stopLoss = StopOrder('SELL', qty, stopPrice=loss_price)
    stopLoss.parentId = parentId
    stopLoss.transmit = True  # Last transmits the chain

    # Place orders
    trade = ib.placeOrder(contract, parent)
    ib.placeOrder(contract, takeProfit)
    ib.placeOrder(contract, stopLoss)

    print("Order was submitted, current status:", trade.orderStatus.status)

    # 7. Wait for it to fill
    ib.sleep(1)
    while trade.isActive():
        ib.waitOnUpdate()

    print("Final status:", trade.orderStatus.status)
    if trade.orderStatus.status == 'Filled':
        print("Filled at average price:", trade.orderStatus.avgFillPrice)

# Useful to stop stop orders and limit orders from conflicting with each other 
def PlaceShortSellBracketOrder(ticker, profitMult, lossMult):
    contract = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(contract)
    
    current_price = GetPriceOfTicker(ticker)
    profit_price = round(current_price * profitMult, 2)
    loss_price   = round(current_price * lossMult, 2)
    qty = GetSharesBuyable(current_price)

    # Get a new orderId for parent
    parentId = ib.client.getReqId()

    # Parent (market sell)
    parent = MarketOrder('SELL', qty)
    parent.orderId = parentId
    parent.transmit = False

    # Take-profit (limit buy)
    takeProfit = LimitOrder('BUY', qty, profit_price)
    takeProfit.parentId = parentId
    takeProfit.transmit = False

    # Stop-loss (stop buy)
    stopLoss = StopOrder('BUY', qty, stopPrice=loss_price)
    stopLoss.parentId = parentId
    stopLoss.transmit = True  # Last one transmits the chain

    # Place orders
    ib.placeOrder(contract, parent)
    ib.placeOrder(contract, takeProfit)
    ib.placeOrder(contract, stopLoss)

    print("Short-sell bracket submitted")

def Quit():
    ib.disconnect()

def GetSharesOwned(ticker):
    # 1. Define the contract (example: Apple stock)
    contract = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(contract)  # Ensures contract details are fetched

    # 2. Get current position for this stock
    positions = ib.positions()
    shares_owned = 0
    for pos in positions:
        if pos.contract.symbol == ticker and pos.contract.secType == 'STK':  # Correct security type + correct ticker
            shares_owned = pos.position
            break

    return shares_owned

# returns shares buyable
def GetSharesBuyable(price):
    # 2. Get account balance
    account_info = ib.accountSummary()

    # Extract 'AvailableFunds' for USD (or your currency)
    available_funds_entry = next((row for row in account_info if row.tag == 'AvailableFunds' and row.currency == 'CAD'), None)
    
    available_funds_value = float(available_funds_entry.value)

    if isLive:
        available_funds = available_funds_value * 0.5  # Use 50% of available funds
    else:
        available_funds = (available_funds_value - PaperMoneyStart) * 0.5  # Use 1k plus whatever we've made

    print(f"Available funds: {available_funds}, price: {price}, shares: {available_funds // price}")


    return 1  # Integer number of shares

def GetPriceOfTicker(ticker, timeout=5):
    contract = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(contract)

    ticker2 = yf.Ticker(ticker)
    
    data = ticker2.history(period="1d", interval="1m")

    # Try different price fields in order of reliability
    price = data['Close'].iloc[-1]

    if price is None:
        raise ValueError(f"Could not get market price for {ticker}")

    return float(price)

def Start(live=False):
    ib.connect('127.0.0.1', 4001, clientId=1, timeout=30)
    return
    if live:
        ib.connect('127.0.0.1', 4001, clientId=1, timeout=90)
    else:
        ib.connect('127.0.0.1', 4002, clientId=1)

    #TODO: Make the if else statement more compact/pythonic
    
def print_holdings():
    positions = ib.positions()
    account_info = ib.accountSummary()

    # Extract 'AvailableFunds' for USD (or your currency)
    available_funds_entry = next((row for row in account_info if row.tag == 'AvailableFunds' and row.currency == 'CAD'), None)
    
    available_funds_value = float(available_funds_entry.value)

    print(f"Cash availble: {available_funds_value}")
    if not positions:
        print("You don't currently hold any positions.")
        return

    print("Current portfolio holdings:")
    for pos in positions:
        contract = pos.contract
        position = pos.position  # number of shares
        avg_cost = pos.avgCost

        print(f"{contract.symbol}: {position} shares @ avg cost ${avg_cost:.2f}")

print("TESTING!!!!")

# Example usage