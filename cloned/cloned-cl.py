import streamlit as st
import pandas as pd
import sqlite3
import datetime

# Constants
DB_NAME = "food_log.db"
CSV_FILE = "Indian_Food_Nutrition_Processed.csv"

# Load nutrition data with caching for performance
@st.cache_data
def load_data():
    return pd.read_csv(CSV_FILE)

df = load_data()

# SQLite DB helper functions
def create_food_log_table():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS food_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                dish_name TEXT,
                amount INTEGER,
                calories REAL,
                carbohydrates REAL,
                protein REAL,
                fats REAL,
                free_sugar REAL,
                fibre REAL,
                sodium REAL,
                calcium REAL,
                iron REAL,
                vitamin_c REAL,
                folate REAL
            )
        ''')
        conn.commit()

def add_food_log_entry(entry):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO food_log (date, dish_name, amount, calories, carbohydrates, protein, fats, free_sugar, fibre, sodium, calcium, iron, vitamin_c, folate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', entry)
        conn.commit()

def get_today_log(today_str):
    with sqlite3.connect(DB_NAME) as conn:
        df_log = pd.read_sql_query("SELECT * FROM food_log WHERE date=?", conn, params=(today_str,))
    return df_log

def clear_today_log(today_str):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM food_log WHERE date=?', (today_str,))
        conn.commit()

def get_last_n_days_log(n):
    today = datetime.date.today()
    days = [(today - datetime.timedelta(days=i)).isoformat() for i in range(n)]
    placeholders = ','.join(['?'] * n)
    query = f"SELECT * FROM food_log WHERE date IN ({placeholders}) ORDER BY date DESC"
    with sqlite3.connect(DB_NAME) as conn:
        df_log = pd.read_sql_query(query, conn, params=days)
    return df_log

# Initialize DB and variables
create_food_log_table()
today_str = datetime.date.today().isoformat()

# Streamlit UI
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select Page", ["Add Food & Get Nutrition", "Today's Food Log", "Last 2 Days' Food Log"])

if page == "Add Food & Get Nutrition":

    st.title("Indian Food Calorie & Nutrition Counter 🍽️")
    st.markdown("**Search for food, enter the quantity, and add to your daily log.**")

    search = st.text_input("Search for Dish Name", "")
    amount = st.number_input("Amount eaten (number of servings)", min_value=1, value=1, step=1)

    if search:
        results = df[df["Dish Name"].str.contains(search, case=False, na=False)]
        if not results.empty:
            st.success(f"Found {len(results)} match(es)")
            for idx, row in results.iterrows():
                st.subheader(row["Dish Name"])
                nutrition = {
                    "Calories (kcal)": row["Calories (kcal)"] * amount,
                    "Carbohydrates (g)": row["Carbohydrates (g)"] * amount,
                    "Protein (g)": row["Protein (g)"] * amount,
                    "Fats (g)": row["Fats (g)"] * amount,
                    "Free Sugar (g)": row["Free Sugar (g)"] * amount,
                    "Fibre (g)": row["Fibre (g)"] * amount,
                    "Sodium (mg)": row["Sodium (mg)"] * amount,
                    "Calcium (mg)": row["Calcium (mg)"] * amount,
                    "Iron (mg)": row["Iron (mg)"] * amount,
                    "Vitamin C (mg)": row["Vitamin C (mg)"] * amount,
                    "Folate (µg)": row["Folate (µg)"] * amount,
                }
                st.write(nutrition)
                if st.button(f"Add to Today's Log: {row['Dish Name']} (x{amount})", key=f"add_{idx}_{amount}"):
                    entry = (
                        today_str,
                        row["Dish Name"],
                        amount,
                        nutrition["Calories (kcal)"],
                        nutrition["Carbohydrates (g)"],
                        nutrition["Protein (g)"],
                        nutrition["Fats (g)"],
                        nutrition["Free Sugar (g)"],
                        nutrition["Fibre (g)"],
                        nutrition["Sodium (mg)"],
                        nutrition["Calcium (mg)"],
                        nutrition["Iron (mg)"],
                        nutrition["Vitamin C (mg)"],
                        nutrition["Folate (µg)"],
                    )
                    add_food_log_entry(entry)
                    st.success(f"Added {amount} x {row['Dish Name']} to today's log.")
        else:
            st.warning("No match found! Try typing a different dish name.")
    else:
        st.info("Enter a dish name above to see nutrition facts.")

    with st.expander("See All Foods in Database"):
        st.dataframe(df)

elif page == "Today's Food Log":

    st.title("Today's Food Log & Nutrition Summary")

    log = get_today_log(today_str)
    if log.empty:
        st.info("No foods added yet. Go to the 'Add Food & Get Nutrition' page to add some foods!")
    else:
        display_cols = {
            "dish_name": "Dish Name",
            "amount": "Amount",
            "calories": "Calories (kcal)",
            "carbohydrates": "Carbohydrates (g)",
            "protein": "Protein (g)",
            "fats": "Fats (g)",
            "free_sugar": "Free Sugar (g)",
            "fibre": "Fibre (g)",
            "sodium": "Sodium (mg)",
            "calcium": "Calcium (mg)",
            "iron": "Iron (mg)",
            "vitamin_c": "Vitamin C (mg)",
            "folate": "Folate (µg)",
        }
        display_df = log[list(display_cols.keys())].rename(columns=display_cols)
        st.write("#### Foods Eaten Today:")
        st.dataframe(display_df)

        nutrition_cols = [
            "calories", "carbohydrates", "protein", "fats", "free_sugar",
            "fibre", "sodium", "calcium", "iron", "vitamin_c", "folate"
        ]
        totals = log[nutrition_cols].sum()
        totals_rounded = {display_cols[col]: round(val, 2) for col, val in totals.items()}
        st.write("#### Total Nutrition for Today:")
        st.write(totals_rounded)

        if st.button("Clear Log for Today"):
            clear_today_log(today_str)
            st.success("Today's log cleared! Please refresh the page.")

elif page == "Last 2 Days' Food Log":
    st.title("Food Log: Last 3 Days & Nutrition Summary")
    n_days = 3  # Today + previous 2 days
    log = get_last_n_days_log(n_days)
    if log.empty:
        st.info("No foods logged in the last 3 days.")
    else:
        log['date'] = pd.to_datetime(log['date']).dt.date
        st.write("#### Foods Eaten in Last 3 Days:")
        display_cols = {
            "date": "Date",
            "dish_name": "Dish Name",
            "amount": "Amount",
            "calories": "Calories (kcal)",
            "carbohydrates": "Carbohydrates (g)",
            "protein": "Protein (g)",
            "fats": "Fats (g)",
            "free_sugar": "Free Sugar (g)",
            "fibre": "Fibre (g)",
            "sodium": "Sodium (mg)",
            "calcium": "Calcium (mg)",
            "iron": "Iron (mg)",
            "vitamin_c": "Vitamin C (mg)",
            "folate": "Folate (µg)",
        }
        display_df = log[list(display_cols.keys())].rename(columns=display_cols)
        st.dataframe(display_df)

        st.write("#### Daily Nutrition Totals:")
        grouped = log.groupby('date')
        for day, df_day in grouped:
            totals = df_day[list(display_cols.keys())[3:]].sum()  # nutrition cols only
            totals_rounded = {display_cols[col]: round(val, 2) for col, val in totals.items()}
            st.write(f"**{day}:**")
            st.write(totals_rounded)
