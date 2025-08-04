import streamlit as st
import pandas as pd
import sqlite3
import datetime

DB_NAME = "food_log.db"
CSV_FILE = "Indian_Food_Nutrition_Processed.csv"
CSV_FILE = "cloned/Indian_Food_Nutrition_Processed.csv"
df = pd.read_csv(CSV_FILE)
NUTRITION_COLS = [
    "Calories (kcal)", "Carbohydrates (g)", "Protein (g)", "Fats (g)",
    "Free Sugar (g)", "Fibre (g)", "Sodium (mg)", "Calcium (mg)",
    "Iron (mg)", "Vitamin C (mg)", "Folate (µg)"
]

@st.cache_data
def load_data():
    return pd.read_csv(CSV_FILE)

df = load_data()

def create_db_tables():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS food_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                dish_name TEXT,
                amount REAL,
                amount_unit TEXT,
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
        # Custom per-100g nutrition overrides
        c.execute('''
            CREATE TABLE IF NOT EXISTS custom_grams_nutrition (
                dish_name TEXT PRIMARY KEY,
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

def add_custom_grams_nutrition(dish, values_dict):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO custom_grams_nutrition (
                dish_name, calories, carbohydrates, protein, fats, free_sugar, fibre,
                sodium, calcium, iron, vitamin_c, folate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dish,
            values_dict["Calories (kcal)"],
            values_dict["Carbohydrates (g)"],
            values_dict["Protein (g)"],
            values_dict["Fats (g)"],
            values_dict["Free Sugar (g)"],
            values_dict["Fibre (g)"],
            values_dict["Sodium (mg)"],
            values_dict["Calcium (mg)"],
            values_dict["Iron (mg)"],
            values_dict["Vitamin C (mg)"],
            values_dict["Folate (µg)"],
        ))
        conn.commit()

def get_custom_grams_nutrition(dish):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM custom_grams_nutrition WHERE dish_name=?', (dish,))
        row = c.fetchone()
        if row is None:
            return None
        return dict(zip([d[0] for d in c.description], row))

def add_food_log_entry(entry):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO food_log (
                date, dish_name, amount, amount_unit, calories,
                carbohydrates, protein, fats, free_sugar, fibre,
                sodium, calcium, iron, vitamin_c, folate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

create_db_tables()
today_str = datetime.date.today().isoformat()

st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Select Page",
    ["Add Food & Get Nutrition", "Today's Food Log", "Last 2 Days' Food Log"]
)

if page == "Add Food & Get Nutrition":
    st.title("Food Calorie & Nutrition Counter 🍽️")
    st.markdown("**Search food, choose servings or grams, and add to your daily log.**")

    search = st.text_input("Search for Dish Name", "")
    amount_type = st.radio("Input by:", ["Servings", "Grams"], horizontal=True)
    amount = st.number_input(
        "Amount eaten (number of servings)" if amount_type == "Servings" else "Amount eaten (grams)",
        min_value=1, value=1 if amount_type=="Servings" else 100, step=1
    )

    if search:
        results = df[df["Dish Name"].str.contains(search, case=False, na=False)]
        if not results.empty:
            st.success(f"Found {len(results)} match(es)")
            for idx, row in results.iterrows():
                st.subheader(row["Dish Name"])

                # Use custom override for grams, if exists
                custom_override = get_custom_grams_nutrition(row["Dish Name"]) if amount_type == "Grams" else None

                # Get per100g
                per100g = {col: row[col] for col in NUTRITION_COLS}
                if custom_override is not None:
                    # The first column is dish_name, skip it
                    custom_vals = list(custom_override.values())[1:]
                    for i, col in enumerate(NUTRITION_COLS):
                        per100g[col] = custom_vals[i] if custom_vals[i] is not None else per100g[col]
                    st.info("You have updated values for 'grams' input for this dish! These are being used below.")

                if amount_type == "Servings":
                    scale = amount
                    label = f"servings ({amount})"
                    nutrition = {col: row[col] * scale for col in NUTRITION_COLS}
                else:
                    scale = amount / 100
                    label = f"{amount}g"
                    nutrition = {col: per100g[col] * scale for col in NUTRITION_COLS}

                st.write({col: round(val,2) for col, val in nutrition.items()})

                # Edit override for grams, with saving
                if amount_type == "Grams":
                    with st.expander("Edit/correct nutrition (per 100g for this dish)", expanded=False):
                        vals = {}
                        # Use custom override defaults if available, else CSV
                        if custom_override is not None:
                            custom_vals = list(custom_override.values())[1:]
                            for i, col in enumerate(NUTRITION_COLS):
                                vals[col] = custom_vals[i] if custom_vals[i] is not None else row[col]
                        else:
                            for col in NUTRITION_COLS:
                                vals[col] = row[col]

                        edit_cols = []
                        for col in NUTRITION_COLS:
                            edit_cols.append(st.number_input(
                                f"{col} per 100g",
                                value=float(vals[col]),
                                key=f"{col}_{row['Dish Name']}"
                            ))
                        if st.button("Save/correct values for this food (applies only when using grams)", key=f"edit_{row['Dish Name']}"):
                            add_custom_grams_nutrition(row["Dish Name"], dict(zip(NUTRITION_COLS, edit_cols)))
                            st.success("Your custom per-100g nutrition values for this food have been saved!")

                if st.button(f"Add to Today's Log: {row['Dish Name']} ({label})", key=f"add_{idx}_{amount}_{amount_type}"):
                    entry = (
                        today_str,
                        row["Dish Name"],
                        amount,
                        amount_type,
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
                        nutrition["Folate (µg)"]
                    )
                    add_food_log_entry(entry)
                    st.success(f"Added {row['Dish Name']} ({label}) to today's log.")
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
            "amount_unit": "Unit",
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
            "folate": "Folate (µg)"
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
    n_days = 3
    log = get_last_n_days_log(n_days)
    if log.empty:
        st.info("No foods logged in the last 3 days.")
    else:
        log['date'] = pd.to_datetime(log['date']).dt.date
        display_cols = {
            "date": "Date",
            "dish_name": "Dish Name",
            "amount": "Amount",
            "amount_unit": "Unit",
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
            totals = df_day[list(display_cols.keys())[4:]].sum()
            totals_rounded = {display_cols[col]: round(val, 2) for col, val in totals.items()}
            st.write(f"**{day}:**")
            st.write(totals_rounded)
