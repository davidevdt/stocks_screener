import yfinance as yf
import numpy as np 

def get_wacc(stock: yf.Ticker, risk_free_rate=None, market_return=None, default_risk_free_rate=0.02, default_market_return=0.08, default_cost_of_debt=0.04, default_tax_rate=0.21):
    """
    Function to estimate the WACC. If data is unavailable, uses default values.
    
    Parameters:
    -----------
    stock : yf.Ticker
        The stock info.
    default_... : float
        Default values. 
        
    Returns:
    --------
    discount_rate : float
        The calculated discount rate (WACC).
    """
    
    # 1. Risk-Free Rate (using 10-year US Treasury bond yield as proxy)
    if risk_free_rate is None:
        print(f"Risk-free rate data not available, using default: {default_risk_free_rate}")
        risk_free_rate = default_risk_free_rate
    
    # 2. Market Return (using S&P 500 historical return as proxy)
    if market_return is None:
        print(f"Market return data not available, using default: {default_market_return}")
        market_return = default_market_return
    
    # 3. Cost of Debt (using company's financials)
    try:
        interest_expense = stock.financials.loc['Interest Expense'].iloc[0]  # Interest Expense
        try: 
            total_debt = stock.info['totalDebt']  # Total Debt
        except Exception: 
            total_debt = stock.balance_sheet.loc['Total Debt'].iloc[0]
        cost_of_debt = interest_expense / total_debt  # Cost of Debt
    except Exception as e:
        print(f"Cost of debt data not available, using default: {default_cost_of_debt}")
        total_debt = stock.info['totalDebt']  if 'totalDebt' in stock.info else stock.balance_sheet.loc['Total Debt'].iloc[0]
        cost_of_debt = default_cost_of_debt
    
    # 4. Tax Rate (using company's financials)
    try:
        tax_rate = stock.financials.loc['Tax Rate For Calcs'].iloc[0]
    except Exception:
        try: 
            income_tax_expense = stock.financials.loc['Tax Provision'].iloc[0]
            pre_tax_income = stock.financials.loc['Pretax Income'].iloc[0]
            tax_rate = income_tax_expense / pre_tax_income  # Effective Tax Rate
        except Exception as e:
            print(f"Tax rate data not available, using default: {default_tax_rate}")
            tax_rate = default_tax_rate
    
    # Calculate WACC (Discount Rate)
    try:
        equity_value = stock.info['marketCap']
        total_value = equity_value + total_debt
        cost_of_equity = risk_free_rate + stock.info.get('beta', 1.0) * (market_return - risk_free_rate)
        wacc = (equity_value / total_value) * cost_of_equity + (total_debt / total_value) * cost_of_debt * (1 - tax_rate)
    except Exception as e:
        print("Error calculating WACC, using default values.")
        wacc = (equity_value / total_value) * default_market_return + (total_debt / total_value) * default_cost_of_debt * (1 - default_tax_rate)

    return wacc

def get_discounted_cash_flow(stock: yf.Ticker, risk_free_rate=None, market_return=None, default_risk_free_rate=0.02, default_market_return=0.08, default_cost_of_debt=0.04, default_tax_rate=0.21):
    """
    Calculate the discounted cash flow (DCF) for a given stock, handling various edge cases.
    """
    try:
        fcf = stock.info.get('freeCashflow') if 'freeCashflow' in stock.info else stock.cashflow.loc['Free Cash Flow'].iloc[0]
        if fcf is None:
            return None
    except Exception:
        try:
            fcf = stock.financials.loc['Free Cash Flow'].iloc[0]
            if fcf is None:
                return None
        except Exception:
            print("Unable to retrieve Free Cash Flow data.")
            return None
    
    # Calculate growth rate (g)
    try:
        for try_field in ['Total Revenue', 'Operating Revenue', 'Net Income', 'Basic EPS', 'Diluted EPS']:
            try:
                r_ = stock.financials.loc[try_field].values
            except:
                continue 
            if np.isnan(r_[0]) or r_[0] is None: 
                continue 
            else: 
                if len(r_) >= 2:
                    break 
        revenue = []
        for r in r_: 
            if np.isnan(r) or r is None: 
                break 
            revenue.append(r)
        if len(revenue) < 2:
            print("Insufficient revenue data for growth rate calculation.")
            return None
        start_revenue, end_revenue = revenue[-1], revenue[0]
        years = len(revenue)
        g = (end_revenue / start_revenue) ** (1 / years) - 1
    except Exception as e:
        print(f"Error calculating growth rate: {e}")
        return None
    
    # Get discount rate (r)
    try:
        r = get_wacc(stock, risk_free_rate, market_return, default_risk_free_rate, default_market_return, default_cost_of_debt, default_tax_rate)
        if r is None:
            print("Unable to calculate WACC.")
            return None
    except Exception as e:
        print(f"Error calculating WACC: {e}")
        return None
    
    

    # Handle edge cases
    if fcf <= 0:
        print("Warning: Negative or zero Free Cash Flow. DCF calculation may not be meaningful.")

    if r <= g:
        print("Warning: Growth rate exceeds discount rate. Using alternative calculation.")
        # Use a simplified growth model for 5 years, then terminal value
        future_fcf = fcf * (1 + g) ** 5
        terminal_value = future_fcf / (r - min(g, r - 0.01))  # Ensure r > g for terminal value
        dcf = future_fcf + terminal_value
        return dcf / (1 + r) ** 5  # Discount back to present value
    
    # Standard DCF calculation
    dcf = fcf * (1 + g) / (r - g)
    return dcf
