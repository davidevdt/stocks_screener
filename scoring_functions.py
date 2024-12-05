import pandas as pd
import numpy as np
from scipy import stats

def calculate_scores(df, metrics, show_unweighted=True):
    """
    Calculates weighted scores for all rows in the DataFrame based on specified metrics using vectorized operations.

    Parameters:
    - df: The DataFrame containing the dataset.
    - metrics: A dictionary where keys are metric names and values are dictionaries containing:
        - 'preference' (str): Either 'high' or 'low'.
        - 'weight' (float): The weight to assign to this metric.
        - 'penalize_negative' (bool): Whether negative values should be penalized.
    - show_unweighted: if True, the scores for each metric will be returned unweighted.

    Returns:
    - A DataFrame with individual scores for each metric and the overall weighted score.
    """
    df_ = df.copy()
    if 'Ticker' in df_.columns:
        df_ = df_.set_index('Ticker')
    scores_df = pd.DataFrame(index=df_.index)
    weights = []

    for metric, config in metrics.items():
        preference = config['preference']
        weight = config['weight']
        penalize_negative = config.get('penalize_negative', False)

        if metric in df_.columns and np.issubdtype(df_[metric].dtype, np.number) and weight > 0.0:
            
            # Drop NaNs and optionally penalize negatives
            valid_metric = df_[metric].dropna()
            if penalize_negative:
                valid_metric = valid_metric[valid_metric >= 0]

            # Compute percentiles for the valid metric column
            percentiles = (
                valid_metric.rank(pct=True, method="average") * 100
            )

            # Adjust percentiles for preference
            if preference == 'low':
                percentiles = 100 - percentiles

            # Penalize rows with negative values explicitly if penalize_negative is True
            if penalize_negative:
                percentiles = percentiles.reindex(df_.index, fill_value=np.nan)
                percentiles[df_[metric] < 0] = 0

            # Reindex percentiles to match the original DataFrame
            scores_df[metric + '_Score'] = percentiles.reindex(df_.index, fill_value=np.nan) * weight
            weights.append(weight)

    # Calculate weighted scores
    scores_df["Overall_Score"] = scores_df.sum(axis=1) / sum(weights)

    if show_unweighted:
        for metric, config in metrics.items():
            weight = config['weight']
            if metric + '_Score' in scores_df.columns:
                scores_df[metric + '_Score'] /= weight

    return scores_df

def calculate_sector_scores(df, metrics, show_unweighted=True):
    """
    Calculates sector-specific scores for each row in the DataFrame using vectorized operations.

    Parameters:
    - df: The DataFrame containing the dataset.
    - metrics: A dictionary where keys are metric names and values are dictionaries containing:
        - 'preference' (str): Either 'high' or 'low'.
        - 'weight' (float): The weight to assign to this metric.
        - 'penalize_negative' (bool): Whether negative values should be penalized.
    - show_unweighted: if True, the scores for each metric will be returned unweighted.

    Returns:
    - A DataFrame with 'Sector Score' for each row, relative to its sector.
    """
    if 'Sector' not in df.columns:
        raise ValueError("The DataFrame must contain a 'Sector' column to calculate sector-specific scores.")

    df_ = df.copy()
    if 'Ticker' in df_.columns:
        df_ = df_.set_index('Ticker')
    scores_df = pd.DataFrame(index=df_.index)
    weights = []


    for metric, config in metrics.items():
        preference = config['preference']
        weight = config['weight']
        penalize_negative = config.get('penalize_negative', False)

        if metric in df_.columns and np.issubdtype(df_[metric].dtype, np.number) and weight > 0.0:
            # Create a DataFrame for the metric and sector
            metric_values = df_[[metric, 'Sector']]

            # Mask negative values if penalize_negative is True (temporarily)
            if penalize_negative:
                metric_values.loc[metric_values[metric] < 0, metric] = np.nan

            # Calculate percentiles grouped by sector, handling NaNs properly
            sector_percentiles = metric_values.groupby('Sector')[metric].transform(
                lambda x: pd.Series(
                    stats.rankdata(x.dropna(), method='average') / len(x.dropna()) * 100,
                    index=x.dropna().index
                ).reindex(x.index, fill_value=np.nan)
            )

            # Adjust percentiles for preference (high or low)
            if preference == 'low':
                sector_percentiles = 100 - sector_percentiles

            # Penalize rows with negative values explicitly if penalize_negative is True
            if penalize_negative:
                sector_percentiles[df_[metric] < 0] = 0

            # Weight the scores and store them
            scores_df[metric + '_Sector_Score'] = sector_percentiles * weight
            weights.append(weight)

    # Calculate weighted sector score
    scores_df['Sector_Score'] = scores_df.sum(axis=1) / sum(weights)

    if show_unweighted:
        for metric, config in metrics.items():
            weight = config['weight']
            if metric + '_Sector_Score' in scores_df.columns:
                scores_df[metric + '_Sector_Score'] /= weight

    return scores_df.round(2)

def get_scores(df, metrics, return_merged=True):
    if return_merged:
        scores_df = pd.merge(
            calculate_scores(df, metrics), 
            calculate_sector_scores(df, metrics), 
            left_index=True, right_index=True
        )
        
        return scores_df.round(2)
    else: 
        return calculate_scores(df, metrics), calculate_sector_scores(df, metrics)

def load_scores(df, metrics, from_file=None, to_file=None, return_merged=True):
    
    if not from_file:
        df_scores = get_scores(df, metrics, return_merged=True)
        if to_file is not None:
            df_scores.to_csv(to_file)
            
    else:
        df_scores = pd.read_csv(from_file, index_col=0)
        
        
    if not return_merged: 
        sector_columns = [c for c in df_scores.columns if c.endswith('Sector_Score')]
        df_sector_scores = df_scores.loc[:,sector_columns]
        df_scores = df_scores.loc[:,[c for c in df_scores if c not in sector_columns]]
        return df_scores, df_sector_scores
        
    return df_scores 
        


