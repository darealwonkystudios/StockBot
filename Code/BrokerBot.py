#4002 for paper, 4001 for live.

from ib_insync import IB, Stock, MarketOrder, LimitOrder, StopOrder

ib = IB()
# Given a ticker symbol, buy the stock at market price
def Buy(ticker):
        
    # 1. Define contract
    contract = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(contract)
    
    max_shares = 1

    # 5. Place market order
    if max_shares > 0:
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
    
    shares_owned = GetSharesOwned(ticker)
   
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

# Useful to stop stop orders and limit orders from conflicting with each other 
def PlaceBuyBracketOrder(ticker, profitMult, lossMult):
    contract = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(contract)
    
    current_price = GetPriceOfTicker(ticker)
    profit_price = round(current_price * profitMult, 2)
    loss_price   = round(current_price * lossMult, 2)
    qty = GetSharesBuyable(current_price)

    parent = MarketOrder('BUY', qty)
    parent.transmit = False

    takeProfit = LimitOrder('SELL', qty, profit_price)
    takeProfit.parentId = parent.orderId
    takeProfit.transmit = False

    stopLoss = StopOrder('SELL', qty, loss_price)
    stopLoss.parentId = parent.orderId
    stopLoss.transmit = True  # Last one transmits the whole chain

    ib.placeOrder(contract, parent)
    ib.placeOrder(contract, takeProfit)
    ib.placeOrder(contract, stopLoss)

# Useful to stop stop orders and limit orders from conflicting with each other 
def PlaceShortSellBracketOrder(ticker, profitMult, lossMult):
    contract = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(contract)
    
    current_price = GetPriceOfTicker(ticker)  # Your own function
    profit_price = round(current_price * profitMult, 2)
    loss_price   = round(current_price * lossMult, 2)
    qty = GetSharesBuyable(current_price)

    parent = MarketOrder('SELL', qty)
    parent.transmit = False

    takeProfit = LimitOrder('BUY', qty, profit_price)
    takeProfit.parentId = parent.orderId
    takeProfit.transmit = False

    stopLoss = StopOrder('BUY', qty, loss_price)
    stopLoss.parentId = parent.orderId
    stopLoss.transmit = True  # Last one transmits the whole chain

    ib.placeOrder(contract, parent)
    ib.placeOrder(contract, takeProfit)
    ib.placeOrder(contract, stopLoss)

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

# Number of shares buyable based on available funds and given current price
def GetSharesBuyable(price):
    # 2. Get account balance
    account_info = ib.accountSummary()
    available_funds = float(account_info.loc['AvailableFunds', 'value'] * 0.0005)  # Use 50% of available funds

    # 4. Calculate max shares (accounting for commissions)
    max_shares = int(available_funds // price)

    return max_shares

def GetPriceOfTicker(ticker):
    # 1. Define the contract (example: Apple stock)
    contract = Stock(ticker, 'SMART', 'USD')
    ib.qualifyContracts(contract)  # Ensures contract details are fetched

    # 2. Get current market price
    market_data = ib.reqMktData(contract)
    ib.sleep(1)  # Wait for price to populate
    price = float(market_data.last if market_data.last else market_data.close)

    return price

def Start(live=False):
    if live:
        ib.connect('127.0.0.1', 4002, clientId=1)
    else:
        ib.connect('127.0.0.1', 4001, clientId=1)

    #TODO: Make the if else statement more compact/pythonic
    
def print_holdings():
    positions = ib.positions()
    
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

Start(live=False)

print("TESTING32!!!!")

Buy("AAPL") 
# Example usage