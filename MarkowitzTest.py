import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import scipy.optimize as optimization

#on average there are 252 trading days a year
NUM_TRADING_DAYS=252
# we will generate random w (different portfolios)
NUM_PORTFOLIOS=10000

#stocks we want to handle

stocks=["AAPL","WMT","TSLA","GE","AMZN","DB"]

#historical data-define START and END dates

start_date="2012-01-01"
end_date="2017-01-01"

def download_data():

    # name of the stock as key-stock values (2010-2017) as the values
    stock_data={}

    for stock in stocks:
        #closing prices
        ticker=yf.Ticker(stock)
        stock_data[stock]=ticker.history(start=start_date,end=end_date)['Close']

    return pd.DataFrame(stock_data)


def show_data(data):
    data.plot(figsize=(10,5))
    plt.show()

def calculate_return(data):

    #NORMALIZATION is why we use the log return and not the noral one-so we have a comparable metric
    log_return=np.log(data/data.shift(1))
    return log_return[1:]

def show_statistics(returns):

    #instead of daily metrics we are after annual metrics
    #mean of annual return
    print(returns.mean()*NUM_TRADING_DAYS)
    print(returns.cov()*NUM_TRADING_DAYS)


def show_mean_variance(returns,weights):
    portfolio_return=np.sum(returns.mean()*weights)*NUM_TRADING_DAYS
    portfolio_volatility=np.sqrt(np.dot(weights.T,np.dot(returns.cov()*NUM_TRADING_DAYS,weights)))

    print("Expected portfolio mean (return): ", portfolio_return)
    print("Expected portfolio volatility (standard deviation: ",portfolio_volatility )

def show_portfolios(returns,volatilities):
    plt.figure(figsize=(10,6))
    plt.scatter(volatilities,returns,c=returns/volatilities,marker="o")
    plt.grid(True)
    plt.xlabel("Expected Volatility")
    plt.ylabel("Expected Return")
    plt.colorbar(label="Sharpe Ratio")
    plt.show()


def generate_portfolios(returns):
    portfolio_means=[]
    portfolio_risks=[]
    portfolio_weights=[]

    for _ in range(NUM_PORTFOLIOS):

        #generate random 1d array for weights
        w = np.random.random(len(stocks))
        w /= np.sum(w)
        portfolio_weights.append(w)
        portfolio_means.append(np.sum(returns.mean()*w)*NUM_TRADING_DAYS)
        portfolio_risks.append(np.sqrt(np.dot(w.T,np.dot(returns.cov()*NUM_TRADING_DAYS,w))))

    return np.array(portfolio_weights),np.array(portfolio_means),np.array(portfolio_risks)

def statistics(weights,returns):
    portfolio_return=np.sum(returns.mean()*weights)*NUM_TRADING_DAYS
    portfolio_volatility=np.sqrt(np.dot(weights.T,np.dot(returns.cov()*NUM_TRADING_DAYS,weights)))

    return np.array([portfolio_return,portfolio_volatility,portfolio_return/portfolio_volatility])

#use scipy module to find the minimum of a given function
#the maximum of f(x) is the minimum of -f(x)
def min_function_sharpe(weights,returns):
    return -statistics(weights,returns)[2]

def optimize_portfolio(weights,returns):
    #the sum of the weights is 1
    constraints={'type':'eq',
                'fun': lambda x:np.sum(x)-1}

    #the weights can be 1 at most: 1 when 100% of the money is invested in one single stock

    bounds=tuple((0,1) for _ in range(len(stocks)))
    return optimization.minimize(fun=min_function_sharpe,x0=weights[0],args=returns,method='SLSQP',bounds=bounds,constraints=constraints)


def print_optimal_portfolio(optimum,returns):
    print("Optimal portfolio: ", optimum['x'].round(3))
    print("Expected return, volatility and Sharpe ratio: ",
          statistics(optimum['x'].round(3),returns))

def show_optimal_portfolio(opt,rets,portfolio_rets,portfolio_vols):
    plt.figure(figsize=(10,6))
    plt.scatter(portfolio_vols,portfolio_rets,c=portfolio_rets/portfolio_vols,marker="o")
    plt.grid(True)
    plt.xlabel("Expected Volatility")
    plt.ylabel("Expected Return")
    plt.colorbar(label="Sharpe Ratio")
    plt.plot(statistics(opt['x'],rets)[1],statistics(opt['x'],rets)[0], 'g*',markersize=20)
    plt.show()


if __name__== "__main__":
    dataset=download_data()
    #show_data(dataset)
    log_daily_returns=calculate_return(dataset)
    #show_mean_variance(log_daily_returns)

    pweights,means,risks=generate_portfolios(log_daily_returns)

    show_portfolios(means,risks)
    optimum=optimize_portfolio(pweights,log_daily_returns)
    print_optimal_portfolio(optimum,log_daily_returns)
    show_optimal_portfolio(optimum,log_daily_returns,means,risks)