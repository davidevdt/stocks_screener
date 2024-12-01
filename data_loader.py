from data_functions import load_data
from scoring_functions import load_scores
from metrics import metrics 

stocks_file_name = "./data/stocks_universe.csv"
scores_file_name = "./data/stocks_scores.csv"

def load_stocks_and_scores_data(
    metrics, 
    tickers=None, 
    stocks_from_file=None, 
    scores_from_file=None, 
    stocks_to_file=None, 
    scores_to_file=None,
    merge_scores=True
):
    df = load_data(tickers=tickers, from_file=stocks_from_file, to_file=stocks_to_file)
    df_scores = load_scores(df, metrics, from_file=scores_from_file, to_file=scores_to_file, return_merged=merge_scores)
    return df, df_scores
    
if __name__ == '__main__':
    
    try: 
        with open("./data/sp500_tickers.txt", "r") as f:
            tickers = [l.strip() for l in f]
            
        with open("./data/other_tickers.txt", "r") as f:
            tickers.extend([l.strip() for l in f])
            
    except Exception as e: 
        tickers = ['AAPL', 'GOOGL', 'BRK.B', 'NVDA', 'NFLX', 'V', 'AMZN']
        
    df,df_scores = load_stocks_and_scores_data(metrics, tickers, None, None, stocks_file_name, scores_file_name, True)
    
    print(df.round(2))