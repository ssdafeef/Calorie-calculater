#!/usr/bin/env python3
"""
Fix for TypeError: unsupported operand type(s) for +: 'float' and 'str'
This script fixes the issue in the calorie calculator where string values
in the database prevent proper summing of nutritional values.
"""

import pandas as pd
import sqlite3
import os

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(SCRIPT_DIR, "food_log.db")

def fix_data_types_in_food_log():
    """Fix data types in food_log table to ensure all numeric columns contain only numbers."""
    with sqlite3.connect(DB_NAME) as conn:
        # Read the data
        df = pd.read_sql_query("SELECT * FROM food_log", conn)
        
        # Identify numeric columns
        numeric_cols = [
            "calories", "carbohydrates", "protein", "fats", "free_sugar", 
            "fibre", "sodium", "calcium", "iron", "vitamin_c", "folate", "creatine"
        ]
        
        # Convert string values to float, handling any non-numeric values
        for col in numeric_cols:
            if col in df.columns:
                # Convert to numeric, replacing non-numeric values with 0.0
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        
        # Update the database with cleaned data
        df.to_sql('food_log_temp', conn, if_exists='replace', index=False)
        
        # Drop old table and rename new one
        c = conn.cursor()
        c.execute("DROP TABLE food_log")
        c.execute("ALTER TABLE food_log_temp RENAME TO food_log")
        conn.commit()
        
        print("✅ Data types fixed successfully!")

def safe_sum_dataframe(df):
    """Safely sum numeric columns in a DataFrame, handling string values."""
    # Select only numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    # If no numeric columns, return empty series
    if len(numeric_cols) == 0:
        return pd.Series(dtype='float64')
    
    # Sum only numeric columns
    return df[numeric_cols].sum()

if __name__ == "__main__":
    fix_data_types_in_food_log()
    print("Data types have been fixed in the food_log table.")
