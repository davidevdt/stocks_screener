from data_functions import load_data
from scoring_functions import load_scores
from metrics import metrics 

stocks_file_name = './data/stocks_fundamentals.csv'
scores_file_name = './data/stocks_scores.csv'

custom_tickers = ['COIN', 'MSTR', 'ASML']


def load_stocks_and_scores_data(
    metrics, 
    custom_tickers=None, 
    stocks_from_file=None, 
    scores_from_file=None, 
    stocks_to_file=None, 
    scores_to_file=None
):
    df = load_data(custom_tickers=custom_tickers, from_file=stocks_from_file, to_file=stocks_to_file)
    df_scores = load_scores(df, metrics, from_file=scores_from_file, to_file=scores_to_file)
    return df, df_scores
    
if __name__ == '__main__':
    df,df_scores = load_stocks_and_scores_data(metrics, custom_tickers, None, None, stocks_file_name, scores_file_name)
    
    print(df.round(2))