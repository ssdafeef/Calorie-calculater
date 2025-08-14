#!/usr/bin/env python3
"""
Fix for TypeError: unsupported operand type(s) for +: 'float' and 'str'
This script fixes the pandas sum() error by ensuring all numeric columns are properly converted.
"""

import pandas as pd
import numpy as np

def fix_numeric_columns(df, exclude_cols=None):
    """
    Fix numeric columns in a DataFrame by converting string values to float.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        exclude_cols (list): List of column names to exclude from conversion
    
    Returns:
        pd.DataFrame: DataFrame with fixed numeric columns
    """
    if exclude_cols is None:
        exclude_cols = []
    
    df_fixed = df.copy()
    
    # Get numeric columns (exclude specified columns)
    numeric_cols = [col for col in df.columns if col not in exclude_cols]
    
    for col in numeric_cols:
        try:
            # Convert to numeric, handling errors
            df_fixed[col] = pd.to_numeric(df_fixed[col], errors='coerce')
            # Fill NaN values with 0.0
            df_fixed[col] = df_fixed[col].fillna(0.0)
        except Exception as e:
            print(f"Warning: Could not convert column {col}: {e}")
            df_fixed[col] = 0.0
    
    return df_fixed

def safe_sum_columns(df, exclude_cols=None):
    """
    Safely sum columns in a DataFrame, handling type conversion issues.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        exclude_cols (list): List of column names to exclude from summing
    
    Returns:
        pd.Series: Sum of numeric columns
    """
    if exclude_cols is None:
        exclude_cols = []
    
    # Fix numeric columns first
    df_fixed = fix_numeric_columns(df, exclude_cols)
    
    # Get columns to sum
    sum_cols = [col for col in df_fixed.columns if col not in exclude_cols]
    
    # Return sum
    return df_fixed[sum_cols].sum()

# Example usage for the specific error in cloned-cl.py
def fix_daily_totals_calculation(df_day):
    """
    Fix the daily totals calculation that was causing the TypeError.
    
    Args:
        df_day (pd.DataFrame): Daily food log DataFrame
    
    Returns:
        pd.Series: Fixed daily totals
    """
    # Columns to exclude from summing
    exclude_cols = ["id", "date", "dish_name", "amount", "amount_unit"]
    
    # Use the safe sum function
    return safe_sum_columns(df_day, exclude_cols)

if __name__ == "__main__":
    # Test the fix
    print("Type Error Fix - Ready to use")
    print("Import this module and use fix_daily_totals_calculation()")
