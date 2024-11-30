import yfinance as yf
import numpy as np
import pandas as pd 
from datetime import datetime, timedelta
from helper_functions import get_peg_ratio, get_growth_factors
from discount_cash_flow import get_discounted_cash_flow
import time 

TIME_SLEEP = 1.2

column_order = [
	'Ticker',
	'Company',
	'Exchange',
	'Sector',
	'Industry',
	'Country',
	'Price',
	'Target Price',
	'Market Cap',
	'Beta',
	'P/E',
	'Forward P/E',
	'PEG',
	'Forward PEG',
	'P/S',
	'P/B',
	'EV/EBITDA',
	'Price/Free Cash Flow', 
	'Discounted Cash Flow',
	'DCF Per Share',
	'DCF Ratio',
	'EPS growth',
	'EPS growth quarter', 
	'Revenue growth', 
	'LastYear Revenue Growth (CAGR)',
	'LastYear Revenue YoY Growth Change',
	'LastYear Net Income Growth (CAGR)',
	'LastYear Net Income YoY Growth Change',
	'LastQuarter Revenue Growth (CAGR)',
	'LastQuarter Revenue Quarter Growth Change',
	'LastQuarter Net Income Growth (CAGR)',
	'LastQuarter Net Income Quarter Growth Change',
	'LastQuarter Revenue YoY Growth Change',
    'LastQuarter Net Income YoY Growth Change',
	'Dividend Yield',
	'ROA', 
	'ROE',
	'ROI', 
	'Current Ratio',
	'Quick Ratio',
	'Debt/Equity', 
	'Gross Margin', 
	'Operating Margin', 
	'Profit Margin', 
	'Payout Ratio', 
	'Insider Ownership', 
	'Institutional Ownership', 
	'Institutional Transactions', 
	'Float Short', 
	'Shares Outstanding',
	'Float',
	'Analyst Recom.',
	'Average Volume',
    'Current Volume',
	'20-Day Simple Moving Average',
	'50-Day Simple Moving Average',
	'200-Day Simple Moving Average',
	'Daily Last Close',
	'Yearly Volume/Market Cap',
	'Daily Last Change',
	'Daily Last Change from Open',
	'20-Day High/Low',
	'50-Day High/Low',
	'52-Week High/Low',
	'Daily 1m Price Change',
	'Daily 3m Price Change',
	'Daily 6m Price Change',
	'Daily 12m Price Change',
	'Performance Y',
	'Performance 6M',
	'Volatility',
	'Daily RSI (14)',
	'Monthly RSI (14)'
]

def get_sp500_tickers():
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    return sp500['Symbol'].tolist()

def get_stock_data(ticker, risk_free_rate=None, market_return=None):
    stock = yf.Ticker(ticker)
    info = stock.info
    data = {
        'Ticker': ticker,
        'Company': info.get('longName', ''),
        'Exchange': info.get('exchange', ''),
        'Sector': info.get('sector', ''),
        'Industry': info.get('industry', ''),
        'Country': info.get('country', ''),
        'Market Cap': info.get('marketCap', np.nan),
        'P/E': info.get('trailingPE', np.nan),
        'Forward P/E': info.get('forwardPE', np.nan),
        'PEG': info.get('trailingPegRatio', np.nan) if info.get('trailingPegRatio') else get_peg_ratio(stock),
        'Forward PEG': get_peg_ratio(stock, trailing=False), 
        'P/S': info.get('priceToSalesTrailing12Months', np.nan),
        'P/B': info.get('priceToBook', np.nan),
        'EV/EBITDA': info.get('enterpriseToEbitda', np.nan),
        'Price/Free Cash Flow': info.get('marketCap', np.nan) / info.get('freeCashflow', np.nan) if info.get('freeCashflow') else np.nan,
        'EPS growth': info.get('earningsGrowth', np.nan),
        'EPS growth quarter': info.get('earningsQuarterlyGrowth', np.nan),  
        'Revenue growth': info.get('revenueGrowth', np.nan),  
        'Dividend Yield': info.get('dividendYield', 0.0),
        'ROA': info.get('returnOnAssets', np.nan),
        'ROE': info.get('returnOnEquity', np.nan),
        'ROI': info.get('returnOnEquity', np.nan),  # Approximation
        'Current Ratio': info.get('currentRatio', np.nan),
        'Quick Ratio': info.get('quickRatio', np.nan),
        'Debt/Equity': info.get('debtToEquity', np.nan),
        'Gross Margin': info.get('grossMargins', np.nan),
        'Operating Margin': info.get('operatingMargins', np.nan),
        'Profit Margin': info.get('profitMargins', np.nan),
        'Payout Ratio': info.get('payoutRatio', np.nan),
        'Insider Ownership': info.get('heldPercentInsiders', np.nan),
        'Institutional Ownership': info.get('heldPercentInstitutions', np.nan),
        'Institutional Transactions': np.nan,  # Not available in yfinance
        'Float Short': info.get('shortPercentOfFloat', np.nan),
        'Analyst Recom.': info.get('recommendationMean', np.nan),
        'Earnings Date': info.get('earningsTimestamp', np.nan),
        'Beta': info.get('beta', np.nan),
        'Average Volume': info.get('averageVolume', np.nan),
        'Current Volume': info.get('volume', np.nan),
        'Price': info.get('currentPrice', np.nan),
        'Target Price': info.get('targetMeanPrice', np.nan),
        'IPO Date': info.get('firstTradeDateEpochUtc', np.nan),
        'Shares Outstanding': info.get('sharesOutstanding', np.nan),
        'Float': info.get('floatShares', np.nan),
        'Discounted Cash Flow': get_discounted_cash_flow(stock, risk_free_rate, market_return)
    }
    
    data['DCF Per Share'] = data['Discounted Cash Flow'] / data['Shares Outstanding'] if data['Shares Outstanding'] else np.nan 
    data['DCF Ratio'] = data['Market Cap'] / data['Discounted Cash Flow'] if data['Discounted Cash Flow'] > 0.0 else np.inf
        
    growth_factors = get_growth_factors(stock, quarterly=False)
    quarteerly_growth_factors = get_growth_factors(stock, quarterly=True)
    for k,v in growth_factors.items():
        data[k] = v
    for k,v in quarteerly_growth_factors.items():
        data[k] = v
    
    # Get historical data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*5)  # 5 years of data
    hist = stock.history(start=start_date, end=end_date)
    hist_mo = stock.history(period="max", interval="1mo")
    
    # Calculate moving averages
    for window in [20, 50, 200]:
        data[f'{window}-Day Simple Moving Average'] = hist['Close'].rolling(window=window).mean().iloc[-1]
    
    data['Daily Last Close'] = hist['Close'].iloc[-1]
    
    # Calculate volume metrics
    data['Yearly Volume/Market Cap'] = hist['Volume'].sum() / data['Market Cap'] if data['Market Cap'] else np.nan
    
    # Calculate price changes
    data['Daily Last Change'] = hist['Close'].pct_change().iloc[-1]
    data['Daily Last Change from Open'] = (hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1]
    
    # Calculate high/low metrics
    data['20-Day High/Low'] = f"{hist['High'].rolling(window=20).max().iloc[-1]:.2f}/{hist['Low'].rolling(window=20).min().iloc[-1]:.2f}"
    data['50-Day High/Low'] = f"{hist['High'].rolling(window=50).max().iloc[-1]:.2f}/{hist['Low'].rolling(window=50).min().iloc[-1]:.2f}"
    data['52-Week High/Low'] = f"{hist['High'].rolling(window=252).max().iloc[-1]:.2f}/{hist['Low'].rolling(window=252).min().iloc[-1]:.2f}"
    
    
    for period in [1, 3, 6, 12]:
        data[f'Daily {period}m Price Change'] = hist['Close'].pct_change(periods=period*20).iloc[-1]
    
    
    # Calculate performance
    data['Performance Y'] = hist['Close'].pct_change(periods=252).iloc[-1]  # 1-year performance
    data['Performance 6M'] = hist['Close'].pct_change(periods=126).iloc[-1]  # 6-month performance
    
    # Calculate volatility
    data['Volatility'] = hist['Close'].pct_change().rolling(window=252).std().iloc[-1] * (252 ** 0.5)  # Annualized volatility
    
    # Calculate RSI
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['Daily RSI (14)'] = 100 - (100 / (1 + rs.iloc[-1]))
    
    delta_mo = hist_mo['Close'].diff()
    gain_mo = (delta_mo.where(delta_mo > 0, 0)).rolling(window=14).mean()
    loss_mo = (-delta_mo.where(delta_mo < 0, 0)).rolling(window=14).mean()
    rs_mo = gain_mo / loss_mo
    hist_mo
    data['Monthly RSI (14)'] = 100 - (100 / (1 + rs_mo.iloc[-1]))
    
    return data


def load_data(tickers=None, from_file=None, to_file='./data/stocks_fundamentals.csv'):
    
    if from_file is None and tickers is None:
        tickers = ['AAPL', 'GOOGL', 'BRK.B', 'NVDA', 'NFLX', 'V', 'AMZN']
    
    if from_file is None:
        data = []
        
        # These will be used for discounted cash flow model valuation
        treasury_data = yf.Ticker("^TNX").history(period="1d")
        market_history = yf.Ticker("^GSPC").history() 
        risk_free_rate = treasury_data['Close'].iloc[0] / 100
        market_return = market_history['Close'].pct_change().mean() * 252
        
        for i,ticker in enumerate(tickers):
            if '.' in ticker:
                ticker = ticker.replace('.', '-')
            print(f'Ticker:{ticker} -- {i} out of {len(tickers)}')
            try:
                stock_data = get_stock_data(ticker, risk_free_rate, market_return)
                data.append(stock_data)
            except Exception as e:
                print(f"Error processing {ticker}: {e}")
            
            time.sleep(TIME_SLEEP)

        # Create DataFrame
        df = pd.DataFrame(data).round(2)
        
        if to_file is not None:
            df.loc[:, column_order].to_csv(to_file, index=False)
    else: 
        df = pd.read_csv(from_file)
        
    return df.loc[:,column_order]