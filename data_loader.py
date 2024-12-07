from data_functions import load_data
from scoring_functions import load_scores
import json 

def load_stocks_and_scores_data(
    metrics, 
    tickers=None, 
    stocks_from_file=None, 
    scores_from_file=None, 
    stocks_to_file=None, 
    scores_to_file=None,
    merge_scores=True
):
    df = load_data(tickers=tickers, from_file=stocks_from_file, to_file=stocks_to_file).set_index('Ticker')
    df_scores = load_scores(df, metrics, from_file=scores_from_file, to_file=scores_to_file, return_merged=merge_scores)
    
    if merge_scores:
        return df, df_scores
    else:
        df_global_scores,df_sector_scores = df_scores
        return df, df_global_scores, df_sector_scores
        
    
if __name__ == '__main__':
    
    stocks_file_name = "./data/stocks_universe.csv"
    scores_file_name = "./data/stocks_scores.csv"
    metrics_config_file_name = "./metrics_config/default_metrics.json"
    
    try: 
        with open("./data/sp500_tickers.txt", "r") as f:
            tickers = [l.strip() for l in f]
            
        with open("./data/other_tickers.txt", "r") as f:
            tickers.extend([l.strip() for l in f])
            
    except Exception as e: 
        tickers = ['AAPL', 'GOOGL', 'BRK.B', 'NVDA', 'NFLX', 'V', 'AMZN']
        
    with open(metrics_config_file_name, 'r') as f:
        metrics = json.load(f)
    
    df,df_scores = load_stocks_and_scores_data(metrics, tickers, None, None, stocks_file_name, scores_file_name, True)
    
    print(df.columns)