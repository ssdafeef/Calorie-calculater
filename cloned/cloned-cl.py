import streamlit as st
import pandas as pd
import sqlite3
import datetime
import calendar
import os

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(SCRIPT_DIR, "food_log.db")
SERVINGS_CSV_FILE = os.path.join(SCRIPT_DIR, "Indian_Food_Nutrition_Processed.csv")
GRAMS_CSV_FILE = os.path.join(SCRIPT_DIR, "newdb.csv")
NUTRITION_COLS = [
    "Calories (kcal)", "Carbohydrates (g)", "Protein (g)", "Fats (g)",
    "Free Sugar (g)", "Fibre (g)", "Sodium (mg)", "Calcium (mg)",
    "Iron (mg)", "Vitamin C (mg)", "Folate (µg)", "Creatine (g)"
]

@st.cache_data
def load_data(dataset_type):
    if dataset_type == "Servings":
        return pd.read_csv(SERVINGS_CSV_FILE)
    else:
        return pd.read_csv(GRAMS_CSV_FILE)

df = load_data("Servings")

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
                folate REAL,
                creatine REAL
            )
        ''')
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

def add_creatine_column_if_missing():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("PRAGMA table_info(food_log)")
        columns = [col[1] for col in c.fetchall()]
        if "creatine" not in columns:
            c.execute("ALTER TABLE food_log ADD COLUMN creatine REAL")
            conn.commit()

create_db_tables()
add_creatine_column_if_missing()

today_str = datetime.date.today().isoformat()

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
                sodium, calcium, iron, vitamin_c, folate, creatine
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

# === STREAMLIT APP ===
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Select Page",
    ["Add Food & Get Nutrition", "Today's Food Log", "Last 2 Days' Food Log", "Monthly Calendar View"]
)

if page == "Add Food & Get Nutrition":
    st.title("Food Calorie & Nutrition Counter 🍽️")
    st.markdown("**Search food, choose servings or grams, and add to your daily log.**")

    st.subheader("Add Creatine")
    creatine_amount = st.number_input("Amount of Creatine (g)", min_value=0, value=0, step=1)
    if st.button("Add Creatine to Today's Log"):
        if creatine_amount > 0:
            entry = (
                today_str,
                "Creatine",
                creatine_amount,
                "Creatine (g)",
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, creatine_amount
            )
            add_food_log_entry(entry)
            st.success(f"Added {creatine_amount}g of Creatine to today's log.")
        else:
            st.warning("Please enter a positive amount of creatine.")

    search = st.text_input("Search for Dish Name", "")
    amount_type = st.radio("Input by:", ["Servings", "Grams"], horizontal=True)
    amount = st.number_input(
        "Amount eaten (number of servings)" if amount_type == "Servings" else "Amount eaten (grams)",
        min_value=1, value=1 if amount_type == "Servings" else 100, step=1
    )

    df = load_data(amount_type)

    if search:
        results = df[df["Dish Name"].str.contains(search, case=False, na=False)]
        if not results.empty:
            st.success(f"Found {len(results)} match(es)")
            for idx, row in results.iterrows():
                st.subheader(row["Dish Name"])
                custom_override = get_custom_grams_nutrition(row["Dish Name"]) if amount_type == "Grams" else None
                per100g = {col: row[col] for col in NUTRITION_COLS}
                if custom_override is not None:
                    custom_vals = list(custom_override.values())[1:]
                    for i, col in enumerate(NUTRITION_COLS):
                        per100g[col] = custom_vals[i] if custom_vals[i] is not None else per100g[col]
                    st.info("You have updated values for 'grams' input for this dish!")

                if amount_type == "Servings":
                    scale = amount
                    label = f"servings ({amount})"
                    nutrition = {col: row[col] * scale for col in NUTRITION_COLS}
                else:
                    scale = amount / 100
                    label = f"{amount}g"
                    nutrition = {col: per100g[col] * scale for col in NUTRITION_COLS}

                st.write({col: round(val, 2) for col, val in nutrition.items()})

                if amount_type == "Grams":
                    with st.expander("Edit/correct nutrition (per 100g)", expanded=False):
                        vals = {}
                        if custom_override is not None:
                            custom_vals = list(custom_override.values())[1:]
                            for i, col in enumerate(NUTRITION_COLS):
                                vals[col] = custom_vals[i] if custom_vals[i] is not None else row[col]
                        else:
                            for col in NUTRITION_COLS:
                                vals[col] = row[col]

                        edit_cols = []
                        for col in NUTRITION_COLS:
                            if col == "Creatine (g)":
                                continue
                            edit_cols.append(st.number_input(
                                f"{col} per 100g", value=float(vals[col]), key=f"{col}_{row['Dish Name']}"
                            ))

                        if st.button("Save/correct values (grams only)", key=f"edit_{row['Dish Name']}"):
                            add_custom_grams_nutrition(row["Dish Name"], dict(zip(NUTRITION_COLS[:-1], edit_cols)))
                            st.success("Saved custom per-100g values!")

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
                        nutrition["Folate (µg)"],
                        0.0  # creatine (only added explicitly)
                    )
                    add_food_log_entry(entry)
                    st.success(f"Added {row['Dish Name']} ({label}) to today's log.")
        else:
            st.warning("No match found!")
    else:
        st.info("Enter a dish name above to see nutrition facts.")

    with st.expander("See All Foods in Database"):
        st.dataframe(df)

elif page == "Today's Food Log":
    st.title("Today's Food Log & Nutrition Summary")
    log = get_today_log(today_str)
    if log.empty:
        st.info("No foods added yet.")
    else:
        display_cols = {
            "dish_name": "Dish Name", "amount": "Amount", "amount_unit": "Unit",
            "calories": "Calories (kcal)", "carbohydrates": "Carbohydrates (g)",
            "protein": "Protein (g)", "fats": "Fats (g)", "free_sugar": "Free Sugar (g)",
            "fibre": "Fibre (g)", "sodium": "Sodium (mg)", "calcium": "Calcium (mg)",
            "iron": "Iron (mg)", "vitamin_c": "Vitamin C (mg)", "folate": "Folate (µg)",
            "creatine": "Creatine (g)"
        }
        st.dataframe(log[list(display_cols.keys())].rename(columns=display_cols))
        totals = log[[col for col in display_cols.keys() if col not in ("dish_name", "amount", "amount_unit")]].sum()
        st.write("#### Total Nutrition for Today:")
        st.write({display_cols[col]: round(val, 2) for col, val in totals.items()})
        if st.button("Clear Log for Today"):
            clear_today_log(today_str)
            st.success("Today's log cleared! Please refresh.")

elif page == "Last 2 Days' Food Log":
    st.title("Food Log: Last 3 Days & Nutrition Summary")
    log = get_last_n_days_log(3)
    if log.empty:
        st.info("No food logs for the past 3 days.")
    else:
        log['date'] = pd.to_datetime(log['date']).dt.date
        grouped = log.groupby('date')
        for day, df_day in grouped:
            st.write(f"### {day}")
            st.dataframe(df_day)
            totals = df_day.drop(columns=["id", "date", "dish_name", "amount", "amount_unit"]).sum()
            st.write("**Nutrition Totals:**")
            st.write({col: round(val, 2) for col, val in totals.items()})

elif page == "Monthly Calendar View":
    st.title("Monthly Calendar View")
    today = datetime.date.today()
    year = st.sidebar.number_input("Year", min_value=2000, max_value=2100, value=today.year)
    month = st.sidebar.number_input("Month", min_value=1, max_value=12, value=today.month)

    first_day = datetime.date(year, month, 1)
    last_day = datetime.date(year, month, calendar.monthrange(year, month)[1])

    with sqlite3.connect(DB_NAME) as conn:
        query = """
            SELECT * FROM food_log
            WHERE date BETWEEN ? AND ?
            ORDER BY date
        """
        df_month = pd.read_sql_query(query, conn, params=(first_day.isoformat(), last_day.isoformat()))

    if df_month.empty:
        st.info("No food logs found for this month.")
    else:
        df_month['date'] = pd.to_datetime(df_month['date']).dt.date
        db_nutrition_cols = [
            "calories", "carbohydrates", "protein", "fats",
            "free_sugar", "fibre", "sodium", "calcium",
            "iron", "vitamin_c", "folate"
        ]
        daily_totals = df_month.groupby('date')[db_nutrition_cols].sum()
        cal = calendar.Calendar()
        month_days = cal.monthdatescalendar(year, month)
        cal_data = []
        for week in month_days:
            week_data = []
            for day in week:
                if day.month == month:
                    if day in daily_totals.index:
                        totals = daily_totals.loc[day]
                        day_str = f"{day.day}\n"
                        for col in db_nutrition_cols:
                            day_str += f"{col}: {round(totals[col], 2)}\n"
                        week_data.append(day_str)
                    else:
                        week_data.append(f"{day.day}\nNo data")
                else:
                    week_data.append("")
            cal_data.append(week_data)
        df_cal = pd.DataFrame(cal_data, columns=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        st.table(df_cal)
