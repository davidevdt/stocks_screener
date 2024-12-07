import pandas as pd 
import numpy as np 
import yfinance as yf 

def get_peg_ratio(stock, trailing=True):
    
    # Get the PE ratio (Price-to-Earnings ratio)
    if trailing:
        pe_ratio = stock.info.get('trailingPE', None)
        if pe_ratio is None: 
            try:
                pe_ratio = stock.info['currentPrice']/stock.earnings_history['epsActual'].iloc[-1]
            except Exception as e: 
                pe_ratio = stock.info['currentPrice']/stock.financials.loc['Basic EPS'].iloc[0]
    else: 
        pe_ratio = stock.info.get('forwardPE')
        
    # Get the earnings growth rate (annual)
    # earnings_growth = stock.info.get('earningsGrowth', None)
    # earnings_growth = (stock.financials.loc['Net Income'].iloc[0]-stock.financials.loc['Net Income'].iloc[1])/np.abs(stock.financials.loc['Net Income'].iloc[1])
    quarter_earnings = stock.quarterly_financials.loc['Net Income']
    earnings_growth = (quarter_earnings.iloc[0] - quarter_earnings.iloc[3]) / np.abs(quarter_earnings.iloc[3])
    
    if np.isnan(earnings_growth) or earnings_growth is None:
        earnings_growth = stock.info.get('earningsGrowth', None)
        
    # Check if both PE ratio and earnings growth are available
    if pe_ratio is not None and earnings_growth is not None and earnings_growth != 0:
        # Calculate the PEG ratio
        peg_ratio = pe_ratio / earnings_growth
        return peg_ratio
    else:
        print(f"Data for PEG ratio not available or earnings growth is zero for {stock.info['longName']}.")
        return np.nan
    

def get_growth_factors(stock, quarterly = False):
    results = {}
    prefix = 'LastYear ' if not quarterly else 'LastQuarter '
    for metric in ['Revenue', 'Net Income']:
        v_ = None 
        try:
            if metric == 'Revenue':
                financials = stock.financials if not quarterly else stock.quarterly_financials
                if 'Total Revenue' in financials.index:
                    v_ = financials.loc['Total Revenue']
                elif 'Revenue' in financials.index:
                    v_ = financials.loc['Revenue']
                else:
                    raise KeyError("Revenue not found in financials")
            else: 
                financials = stock.financials
                if 'Net Income' in financials.index:
                    v_ = financials.loc['Net Income']
                else:
                    raise KeyError("Net Income not found in earnings")
                
            values = []
            year_change = []
            for i,v in enumerate(v_):
                if v is None or np.isnan(v) or v_.iloc[i] == 0:
                    break
                values.append(v)
                if i > 0:
                    year_change.append(((v_.iloc[i-1]-v_.iloc[i])/v_.iloc[i]))
            if len(values) > 1:
                growth_rate = (values[0] / values[-1]) ** (1/len(values)) - 1
                results[prefix + f'{metric} Growth (CAGR)'] = np.round(growth_rate,2).real
            else:
                results[prefix +f'{metric} Growth (CAGR)'] = np.nan
            
            if len(year_change) > 1: 
                if not quarterly:
                    results[prefix +f'{metric} YoY Growth Change'] = year_change[0] / year_change[1] - 1
                else: 
                    if len(year_change) >= 4:
                        results[prefix +f'{metric} YoY Growth Change'] = year_change[0] / year_change[3] - 1
                    else:  
                        results[prefix +f'{metric} YoY Growth Change'] = year_change[0] / year_change[-1] - 1 
                    if year_change[1] != 0.0:
                        results[prefix +f'{metric} Quarter Growth Change'] = year_change[0] / year_change[1] - 1 
                    else:
                        results[prefix +f'{metric} Quarter Growth Change'] = np.inf
            else:
                results[prefix +f'{metric} YoY Growth Change'] = np.nan
                results[prefix +f'{metric} Quarter Growth Change'] = np.nan
                
        except Exception as e:
            print(f"Error calculating {metric} Growth: {e}")
            results[prefix + f'{metric} Growth (CAGR)'] = np.nan
            results[prefix +f'{metric} YoY Growth Change'] = np.nan
            results[prefix +f'{metric} Quarter Growth Change'] = np.nan 
    return results 
