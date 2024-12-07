import streamlit as st
from data_loader import load_stocks_and_scores_data
from scoring_functions import load_scores
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd 
import copy 
import json 

stocks_file_name = "./data/stocks_universe.csv"
scores_file_name = "./data/stocks_scores.csv"
metrics_config_file_name = "./metrics_config/default_metrics.json"

st.set_page_config(
    page_title="Customizable Stock Screener",
    page_icon="📈",
    layout="wide",
)

with st.sidebar:
    # Create an expander for links
    with st.expander("Go to...", expanded=False):
        st.page_link("Stocks_Screener.py", label="Overview")
        st.page_link("pages/1_Best_Stocks_Overall.py", label="Best Stocks Overall")
        st.page_link("pages/2_Best_Stocks_Sector.py", label="Best Stocks By Sector")
        st.page_link("pages/3_Stock_Details.py", label="Stock Details")
        st.page_link("pages/4_Comparison.py", label="Stocks Comparison")

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
st.session_state.metrics_default = copy.deepcopy(st.session_state.metrics)

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
    
    st.session_state.stocks_df = stocks_df
    st.session_state.global_scores_df = global_scores_df
    st.session_state.sector_scores_df = sector_scores_df
        
### LOAD SIDEBAR
with st.sidebar:    
    if st.button("Recalculate scores"):
        global_scores_df,sector_scores_df = load_scores(
            df = st.session_state.stocks_df, 
            metrics = st.session_state.metrics, 
            from_file=None, 
            to_file= scores_file_name, 
            return_merged=False
        )
        global_scores_df = global_scores_df.loc[:,['Sector','Overall_Score'] + list(global_scores_df.columns[:-2])]
        sector_scores_df = sector_scores_df.loc[:,['Sector','Sector_Score'] + list(sector_scores_df.columns[:-2])]
        
        st.session_state.global_scores_df = global_scores_df
        st.session_state.sector_scores_df = sector_scores_df
    
    config_file_name = st.text_input("Configuration File Name", "my_configuration")
    if st.button("Save configuration"):
        json.dump(st.session_state.metrics, "./metrics_config/" + config_file_name + ".json")
        
    if st.button("Load configuration"):
        config_raw = st.file_uploader("Choose a configuration file", type="json")
        if config_raw is not None: 
            st.session_state.metrics = json.load(config_raw)
            st.session_state.metrics_default = copy.deepcopy(st.session_state.metrics)
            
    if st.button("Update data"): 
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
        
        st.session_state.stocks_df = stocks_df
        st.session_state.global_scores_df = global_scores_df
        st.session_state.sector_scores_df = sector_scores_df
                
### VISUALIZE STOCKS 

red_to_green = LinearSegmentedColormap.from_list('redgreen', ['red', 'green'])

st.subheader("Stocks Data")
st.dataframe(st.session_state.stocks_df.style.format({col: "{:,.2f}" for col in stocks_df.select_dtypes(include='number').columns}))

### VISUALIZE SCORES OPTIONS
def reset_configuration():
    # Reset metrics to their default values
    st.session_state.metrics = copy.deepcopy(st.session_state.metrics_default)
    for metric, config in st.session_state.metrics.items():
        # Explicitly update widget keys in session_state
        st.session_state[f"{metric}_direction"] = "Low" if config["preference"] == "low" else "High"
        st.session_state[f"{metric}_penalize_negative"] = "True" if config["penalize_negative"] else "False"
        st.session_state[f"{metric}_weight"] = config["weight"]

# Render the scoring configuration
with st.expander("Scoring configuration", expanded=False):
    metrics = copy.deepcopy(st.session_state.metrics)

    for metric, config in metrics.items():
        st.write(f"**{metric}**")

        # Ensure the widgets use the current session_state values
        colA, colB, colC = st.columns(3)
        with colA:
            metrics[metric]["preference"] = st.selectbox(
                "Direction",
                ("Low", "High"),
                index=0 if st.session_state.get(f"{metric}_direction", "low") == "low" else 1,
                key=f"{metric}_direction",
            )
        with colB:
            metrics[metric]["penalize_negative"] = st.selectbox(
                "Penalize Negatives",
                ("True", "False"),
                index=0 if st.session_state.get(f"{metric}_penalize_negative", True) else 1,
                key=f"{metric}_penalize_negative",
            )
        with colC:
            metrics[metric]["weight"] = st.slider(
                "Weight",
                0,
                100,
                st.session_state.get(f"{metric}_weight", config["weight"]),
                key=f"{metric}_weight",
            )

    col1, col2,_,_,_,_ = st.columns(6)
    if col1.button("Update"):
        st.session_state.metrics = copy.deepcopy(metrics)
        st.session_state.metrics_default = copy.deepcopy(st.session_state.metrics)
    if col2.button("Reset", on_click=reset_configuration):
        pass

### VISUALIZE SCORES 

st.subheader("Global Scores Data")
col_1,col_2,_,_ = st.columns(4)
with col_1:
    n_scores = st.number_input("Visualize n scores", 1, len(st.session_state.global_scores_df), 15, key="n_scores")
with col_2:
    sectors_to_view = st.multiselect("Sectors", st.session_state.global_scores_df['Sector'].unique().tolist() + ['All'], default='All')
    
if len(sectors_to_view) == 0:
    sectors_to_view = ['All']
    
if 'All' in sectors_to_view:
    sectors_to_view = ['All']
    df_to_view = st.session_state.global_scores_df
    df_to_view = df_to_view.dropna(axis=1,how='all')
else: 
    df_to_view = st.session_state.global_scores_df.loc[st.session_state.global_scores_df['Sector'].isin(sectors_to_view)]
    df_to_view = df_to_view.dropna(axis=1,how='all')

st.dataframe(df_to_view.sort_values('Overall_Score', ascending=False).iloc[:n_scores].\
    style.background_gradient(cmap=red_to_green, axis=0, vmin=0, vmax=100).format(
    {col: "{:,.2f}" for col in global_scores_df.select_dtypes(include='number').columns}
))

st.subheader("Scores Data By Sector")

col_1a,col_2b,_,_ = st.columns(4)
with col_1a: 
    n_sector_scores = st.number_input("Visualize n scores", 1, len(st.session_state.sector_scores_df), 15, key="n_sector_scores") 
with col_2b:
    sectors_to_view_2 = st.multiselect("Sectors_B", st.session_state.sector_scores_df['Sector'].unique().tolist() + ['All'], default='All')

if len(sectors_to_view_2) == 0:
    sectors_to_view_2 = ['All']

if 'All' in sectors_to_view_2:
    sectors_to_view_2 = ['All']
    df_2_to_view = st.session_state.sector_scores_df
    df_2_to_view = df_2_to_view.dropna(axis=1,how='all')
else:    
    df_2_to_view = st.session_state.sector_scores_df.loc[st.session_state.sector_scores_df['Sector'].isin(sectors_to_view_2)]
    df_2_to_view = df_2_to_view.dropna(axis=1,how='all')

st.dataframe(df_2_to_view.sort_values('Sector_Score', ascending=False).iloc[:n_sector_scores].\
    style.background_gradient(cmap=red_to_green, axis=0, vmin=0, vmax=100).format(
    {col: "{:,.2f}" for col in sector_scores_df.select_dtypes(include='number').columns}
))

