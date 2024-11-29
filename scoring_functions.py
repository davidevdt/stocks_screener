import pandas as pd
import numpy as np
from scipy import stats

def calculate_scores(df, metrics, show_unweighted=True):
    """
    Calculates weighted scores for all rows in the DataFrame based on specified metrics using vectorized operations.

    Parameters:
    - df: The DataFrame containing the dataset.
    - metrics: A list of tuples where each tuple contains:
        - Metric name (string): The column name in the DataFrame.
        - Preference (string): Either 'high' or 'low'.
        - Weight (float): The weight to assign to this metric when calculating the weighted average.
    - show_unweighted: if True, the scores for each metric will be returned unweighted.

    Returns:
    - A Pandas Series containing the weighted scores for all rows in the DataFrame.
    """
    df_ = df.copy().set_index('Ticker')
    scores_df = pd.DataFrame(index=df_.index) 
    
    weights = []

    for metric, preference, weight in metrics:
        if metric in df_.columns and np.issubdtype(df_[metric].dtype, np.number):
            
            # Drop NaNs from the metric for percentile calculation
            valid_metric = df_[metric].dropna()
            
            # Compute percentiles for the entire metric column
            percentiles = (
                valid_metric.rank(pct=True, method="average") * 100
            )   # Converts ranks to percentiles

            # Adjust percentiles for preference
            if preference == "low":
                percentiles = 100 - percentiles
                
            # Reindex percentiles to match the original DataFrame
            scores_df[metric + '_Score'] = percentiles.reindex(df_.index, fill_value=np.nan) * weight
            weights.append(weight)

    # Calculate weighted scores
    scores_df["Overall_Score"] = scores_df.sum(axis=1) / sum(weights)
    
    if show_unweighted: 
        for metric, _, weight in metrics:
            scores_df[metric + '_Score'] /= weight   

    return scores_df

def calculate_sector_scores(df, metrics, show_unweighted=True):
    """
    Calculates sector-specific scores for each row in the DataFrame using vectorized operations.

    Parameters:
    - df: The DataFrame containing the dataset.
    - metrics: A list of tuples where each tuple contains:
        - Metric name (string): The column name in the DataFrame.
        - Preference (string): Either 'high' or 'low'.
        - Weight (float): The weight to assign to this metric when calculating the weighted average.
    - show_unweighted: if True, the scores for each metric will be returned unweighted.

    Returns:
    - A DataFrame with 'Sector Score' for each row, relative to its sector.
    """
    # Check if 'Sector' column exists
    if 'Sector' not in df.columns:
        raise ValueError("The DataFrame must contain a 'Sector' column to calculate sector-specific scores.")

    # Prepare to store the scores and weights for all metrics
    df_ = df.copy().set_index('Ticker')
    scores_df = pd.DataFrame(index=df_.index) 
    weights = []

    for metric, preference, weight in metrics:
        if metric in df.columns and np.issubdtype(df[metric].dtype, np.number):
            # Group by Sector and calculate percentiles for each metric
            sector_percentiles = df_.groupby('Sector')[metric].transform(
                lambda x: stats.rankdata(x, method='average') / len(x) * 100
            )

            # Adjust percentiles for preference (high or low)
            if preference == 'low':
                sector_percentiles = 100 - sector_percentiles

            # Weight the scores and store them
            scores_df[metric + '_Sector_Score'] = sector_percentiles * weight
            weights.append(weight)

    # Calculate weighted sector score
    scores_df['Sector_Score'] = scores_df.sum(axis=1) / sum(weights)

    if show_unweighted: 
        for metric, _, weight in metrics:
            scores_df[metric + '_Sector_Score'] /= weight    

    return scores_df.round(2)

def get_scores(df, metrics):
    scores_df = pd.merge(
        calculate_scores(df, metrics), 
        calculate_sector_scores(df, metrics), 
        left_index=True, right_index=True
    )
    
    return scores_df.round(2)

def load_scores(df, metrics, from_file=None, to_file=None):
    
    if not from_file:
        df_scores = get_scores(df, metrics)
        if to_file is not None:
            df_scores.to_csv(to_file)
            
    else:
        df_scores = pd.read_csv(from_file, index_col=1)
        
    return df_scores 
        


