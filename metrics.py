metrics = [
    # Valuation Metrics
    ('P/E', 'low', 0.8),                     # Price to Earnings ratio (high is less favorable)
    ('Forward P/E', 'low', 0.7),              # Forward Price to Earnings ratio (high is less favorable)
    ('PEG', 'low', 0.9),                      # Price/Earnings to Growth ratio (lower is better)
    ('Forward PEG', 'low', 0.8),              # Forward PEG ratio (lower is better)
    ('P/S', 'low', 0.7),                      # Price to Sales ratio (lower is better)
    ('P/B', 'low', 0.7),                      # Price to Book ratio (lower is better)
    ('EV/EBITDA', 'low', 0.8),                # Enterprise Value / EBITDA (lower is better)
    ('Price/Free Cash Flow', 'low', 0.9),     # Price to Free Cash Flow ratio (lower is better)
    
    # Growth Metrics
    ('EPS growth', 'high', 0.9),              # Earnings Per Share Growth (higher is better)
    ('EPS growth quarter', 'high', 0.7),      # EPS Growth in the last quarter (higher is better)
    ('Revenue growth', 'high', 0.8),          # Revenue Growth (higher is better)
    ('LastYear Revenue Growth (CAGR)', 'high', 0.9), # Revenue Growth CAGR (higher is better)
    ('LastYear Revenue YoY Growth Change', 'high', 0.7),  # Year-over-Year Revenue Growth Change (higher is better)
    ('LastYear Net Income Growth (CAGR)', 'high', 0.9),    # Net Income Growth CAGR (higher is better)
    ('LastYear Net Income YoY Growth Change', 'high', 0.7), # Year-over-Year Net Income Growth Change (higher is better)
    ('LastQuarter Revenue Growth (CAGR)', 'high', 0.8),     # Quarterly Revenue Growth CAGR (higher is better)
    ('LastQuarter Revenue Last Available Growth Change', 'high', 0.7),  # Last quarter's revenue growth change (higher is better)
    ('LastQuarter Net Income Growth (CAGR)', 'high', 0.8),  # Quarterly Net Income Growth (higher is better)
    ('LastQuarter Net Income Last Available Growth Change', 'high', 0.7), # Last quarter's Net Income Growth change (higher is better)

    # Profitability Metrics
    ('ROA', 'high', 0.9),                    # Return on Assets (higher is better)
    ('ROE', 'high', 1.0),                    # Return on Equity (higher is better)
    ('ROI', 'high', 0.9),                    # Return on Investment (higher is better)
    ('Gross Margin', 'high', 0.9),            # Gross Profit Margin (higher is better)
    ('Operating Margin', 'high', 0.9),        # Operating Profit Margin (higher is better)
    ('Profit Margin', 'high', 1.0),           # Net Profit Margin (higher is better)
    
    # Liquidity & Financial Health Metrics
    ('Current Ratio', 'high', 0.8),           # Current Ratio (higher is better, liquidity)
    ('Quick Ratio', 'high', 0.8),             # Quick Ratio (higher is better, liquidity)
    ('Debt/Equity', 'low', 0.9),              # Debt-to-Equity Ratio (lower is better)
    
    # Dividend and Payout Metrics
    ('Dividend Yield', 'high', 0.5),          # Dividend Yield (higher is better for income-focused investors)
    ('Payout Ratio', 'low', 0.6),             # Dividend Payout Ratio (lower is better to ensure sustainability)

    # Market Metrics
    ('Market Cap', 'high', 0.6),              # Market Capitalization (larger is generally better)
    ('Insider Ownership', 'high', 0.5),       # Insider Ownership (higher is better, shows confidence)
    ('Institutional Ownership', 'high', 0.6), # Institutional Ownership (higher is better, shows stability)
    ('Institutional Transactions', 'high', 0.3),  # Institutional Transactions (higher is better)
    ('Float Short', 'low', 0.4),              # Short Float (lower is better, suggests stability)
    ('Analyst Recom.', 'high', 0.5),          # Analyst Recommendations (strong buy is higher, more favorable)
    
    # Volatility and Risk Metrics
    ('Beta', 'low', 0.5),                    # Beta (lower is better, lower volatility compared to market)
    ('Volatility', 'low', 0.5),               # Stock Price Volatility (lower is better)
    
    # Price-related Metrics
    ('Price', 'low', 0.0),                   # Stock Price (this could be less relevant, but included for context)
    ('Target Price', 'high', 0.0),            # Target Price (higher is better, indicates potential growth)
    ('Shares Outstanding', 'low', 0.25),       # Shares Outstanding (lower is better, less dilution)
    ('Float', 'low', 0.4),                    # Float (lower is better, indicates tighter control of stock)
    
    # Moving Averages and Performance
    ('20-Day Simple Moving Average', 'high', 0.0),  # Short-term Price trend (higher is better)
    ('50-Day Simple Moving Average', 'high', 0.0),  # Mid-term Price trend (higher is better)
    ('200-Day Simple Moving Average', 'high', 0.0), # Long-term Price trend (higher is better)
    ('Performance Y', 'high', 0.7),                 # 1-year Performance (higher is better)
    ('Performance 6M', 'high', 0.3),                # 6-month Performance (higher is better)
    
    # Price Change and RSI
    ('Daily RSI (14)', 'low', 0.25),             # Relative Strength Index (low indicates more discount price)
    ('Monthly RSI (14)', 'low', 0.35),            # Monthly RSI (low indicates more discount price)
    ('Daily 1m Price Change', 'low', 0.0),       # 1-month Price Change (low indicates more discount price)
    ('Daily 3m Price Change', 'low', 0.05),       # 3-month Price Change (low indicates more discount price)
    ('Daily 6m Price Change', 'low', 0.15),       # 6-month Price Change (low indicates more discount price)
    ('Daily 12m Price Change', 'low', 0.5),      # 12-month Price Change (low indicates more discount price)
    
    # DCF metrics
    ('Discounted Cash Flow', 'high', 0.0),       # Discounted cash flow (higher is better)
    ('DCF Per Share', 'high', 0.5),              # Discounted cash flow per share (higher is better)
    ('DCF Ratio', 'low', 0.6)                    # MarketCap/DCF ratio (lower is better: a stock might be undervalued)   
]
