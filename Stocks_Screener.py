import streamlit as st
from data_loader import load_stocks_and_scores_data
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd 
import json 

stocks_file_name = "./data/stocks_universe.csv"
scores_file_name = "./data/stocks_scores.csv"
metrics_config_file_name = "./metrics_config/default_metrics.json"

st.set_page_config(
    page_title="Stock Screener App",
    page_icon="📈",
    layout="wide",
)

st.title("Stocks Screener")

### LOAD TICKERS 
try: 
    with open("./data/sp500_tickers.txt", "r") as f:
        tickers = [l.strip() for l in f]
        
    with open("./data/other_tickers.txt", "r") as f:
        tickers.extend([l.strip() for l in f])
        
except Exception as e: 
    tickers = ['AAPL', 'GOOGL', 'BRK.B', 'NVDA', 'NFLX', 'V', 'AMZN']
    
### LOAD METRICS
with open(metrics_config_file_name, "r") as f: 
    metrics = json.load(f)
if "metrics" not in st.session_state: 
    st.session_state.metrics = metrics 

### LOAD DATASETS 
with st.spinner("Loading data... Please wait."):
    try: 
        stocks_df,global_scores_df,sector_scores_df = load_stocks_and_scores_data(
            metrics=st.session_state.metrics,
            tickers=tickers,
            stocks_from_file=stocks_file_name,  
            scores_from_file=scores_file_name,
            stocks_to_file=None,
            scores_to_file=None,
            merge_scores=False
        )
    except Exception as e: 
        stocks_df,global_scores_df,sector_scores_df = load_stocks_and_scores_data(
            metrics=st.session_state.metrics,
            tickers=tickers,
            stocks_from_file=None,  
            scores_from_file=None,
            stocks_to_file=stocks_file_name,
            scores_to_file=scores_file_name,
            merge_scores=False
        )   
    
    global_scores_df = global_scores_df.loc[:,['Sector','Overall_Score'] + list(global_scores_df.columns[:-2])]
    sector_scores_df = sector_scores_df.loc[:,['Sector','Sector_Score'] + list(sector_scores_df.columns[:-2])]
    
    if "stocks_df" not in st.session_state:
        st.session_state.stocks_df = stocks_df
    if "global_scores_df" not in st.session_state:
        st.session_state.global_scores_df = global_scores_df
    if "sector_scores_df" not in st.session_state:
        st.session_state.sector_scores_df = sector_scores_df
        
### VISUALIZE DATASETS 

red_to_green = LinearSegmentedColormap.from_list('redgreen', ['red', 'green'])

st.subheader("Stocks Data")
st.dataframe(st.session_state.stocks_df.style.format({col: "{:,.2f}" for col in stocks_df.select_dtypes(include='number').columns}))


st.subheader("Global Scores Data")
st.dataframe(st.session_state.global_scores_df.style.background_gradient(cmap=red_to_green, axis=0, vmin=0, vmax=100).format(
    {col: "{:,.2f}" for col in global_scores_df.select_dtypes(include='number').columns}
))

st.subheader("Scores Data By Sector")
st.dataframe(st.session_state.sector_scores_df.style.background_gradient(cmap=red_to_green, axis=0, vmin=0, vmax=100).format(
    {col: "{:,.2f}" for col in sector_scores_df.select_dtypes(include='number').columns}
))

