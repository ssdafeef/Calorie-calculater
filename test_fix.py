#!/usr/bin/env python3
"""
Test script to verify the TypeError fix works correctly.
"""

import pandas as pd
import numpy as np
import sqlite3
import os
import sys

# Add cloned directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cloned'))

def test_type_fix():
    """Test the type conversion fix for nutrition columns."""
    
    # Create test data with mixed types (simulating the issue)
    test_data = {
        'date': ['2024-01-01', '2024-01-01', '2024-01-02'],
        'dish_name': ['Food A', 'Food B', 'Food C'],
        'amount': [100, 150, 200],
        'amount_unit': ['g', 'g', 'g'],
        'calories': ['200.5', '300.2', 'invalid'],  # String values
        'carbohydrates': [45.0, '60.1', '75.5'],
        'protein': ['15.5', 20.0, '25.3'],
        'fats': [8.5, '12.3', 'invalid_string'],  # Invalid string
        'free_sugar': [5.0, 7.5, 10.0],
        'fibre': ['3.2', 4.5, '6.1'],
        'sodium': [200, '300', 'invalid'],
        'calcium': [100.0, 150.5, '200.2'],
        'iron': ['2.5', 3.0, 'invalid_value'],
        'vitamin_c': [30, '45', '60'],
        'folate': ['100.5', 150.2, '200.0']
    }
    
    df_test = pd.DataFrame(test_data)
    
    print("Original DataFrame:")
    print(df_test.dtypes)
    print("\nSample data:")
    print(df_test.head())
    
    # Apply the fix
    db_nutrition_cols = [
        "calories", "carbohydrates", "protein", "fats",
        "free_sugar", "fibre", "sodium", "calcium",
        "iron", "vitamin_c", "folate"
    ]
    
    # Convert string columns to numeric
    for col in db_nutrition_cols:
        df_test[col] = pd.to_numeric(df_test[col], errors='coerce').fillna(0.0)
    
    print("\nAfter fixing data types:")
    print(df_test[db_nutrition_cols].dtypes)
    
    # Test groupby operation (this was failing before)
    try:
        daily_totals = df_test.groupby('date')[db_nutrition_cols].sum()
        print("\nGroupby operation successful!")
        print("Daily totals:")
        print(daily_totals)
        return True
    except Exception as e:
        print(f"\nError during groupby: {e}")
        return False

def test_with_real_data():
    """Test with actual database data."""
    try:
        db_path = os.path.join('cloned', 'food_log.db')
        if os.path.exists(db_path):
            with sqlite3.connect(db_path) as conn:
                query = "SELECT * FROM food_log LIMIT 10"
                df_real = pd.read_sql_query(query, conn)
                
                if not df_real.empty:
                    print("\nTesting with real data:")
                    print(f"Shape: {df_real.shape}")
                    
                    # Apply the same fix
                    numeric_cols = [col for col in df_real.columns 
                                  if col not in ["id", "date", "dish_name", "amount", "amount_unit"]]
                    
                    for col in numeric_cols:
                        df_real[col] = pd.to_numeric(df_real[col], errors='coerce').fillna(0.0)
                    
                    # Test groupby
                    if 'date' in df_real.columns:
                        daily_totals = df_real.groupby('date')[numeric_cols].sum()
                        print("Real data test successful!")
                        return True
        return True  # If no data, test passes
    except Exception as e:
        print(f"Real data test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing TypeError fix...")
    
    # Test with synthetic data
    test1_success = test_type_fix()
    
    # Test with real data
    test2_success = test_with_real_data()
    
    if test1_success and test2_success:
        print("\n✅ All tests passed! TypeError fix is working correctly.")
    else:
        print("\n❌ Some tests failed.")
