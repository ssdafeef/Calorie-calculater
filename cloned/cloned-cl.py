import streamlit as st
import pandas as pd
import sqlite3
import datetime
import calendar
import os
import plotly.graph_objects as go

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(SCRIPT_DIR, "food_log.db")
SERVINGS_CSV_FILE = os.path.join(SCRIPT_DIR, "Indian_Food_Nutrition_Processed.csv")
GRAMS_CSV_FILE = os.path.join(SCRIPT_DIR, "newdb.csv")
NUTRITION_COLS = [
    "Calories (kcal)", "Carbohydrates (g)", "Protein (g)", "Fats (g)",
    "Free Sugar (g)", "Fibre (g)", "Sodium (mg)", "Calcium (mg)",
    "Iron (mg)", "Vitamin C (mg)", "Folate (µg)", "Creatine(g)"
]

# Sci-fi theme configuration
st.set_page_config(
    page_title="🚀 NUTRITION OS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for sci-fi theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --neon-cyan: #00ffff;
        --neon-purple: #ff00ff;
        --neon-green: #39ff14;
        --dark-bg: #0a0a0a;
        --panel-bg: #1a1a2e;
        --grid-color: #16213e;
    }
    
    /* Global styles */
    .main {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #0f0f23 0%, #16213e 100%);
        border-right: 1px solid var(--neon-cyan);
    }
    
    /* Headers with neon glow */
    h1 {
        color: var(--neon-cyan);
        text-shadow: 0 0 10px var(--neon-cyan), 0 0 20px var(--neon-cyan);
        font-family: 'Courier New', monospace;
        letter-spacing: 2px;
    }
    
    h2, h3 {
        color: var(--neon-purple);
        text-shadow: 0 0 5px var(--neon-purple);
        font-family: 'Courier New', monospace;
    }
    
    /* Buttons with cyberpunk styling */
    .stButton > button {
        background: linear-gradient(45deg, var(--neon-cyan), var(--neon-purple));
        color: #000;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    }
    
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(255, 0, 255, 0.8);
        transform: translateY(-2px);
    }
    
    /* Input fields with holographic effect */
    .stTextInput > div > div > input {
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid var(--neon-cyan);
        border-radius: 5px;
        color: var(--neon-cyan);
        font-family: 'Courier New', monospace;
    }
    
    /* Dataframes with matrix styling */
    .dataframe {
        background: rgba(0, 255, 255, 0.05);
        border: 1px solid var(--neon-cyan);
        color: #ffffff;
    }
    
    /* Metrics with digital display */
    .metric {
        background: linear-gradient(135deg, rgba(0, 255, 255, 0.1), rgba(255, 0, 255, 0.1));
        border: 1px solid var(--neon-cyan);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(57, 255, 20, 0.1);
        border: 1px solid var(--neon-green);
        border-radius: 5px;
        color: var(--neon-green);
    }
    
    /* Success/Warning messages */
    .stSuccess {
        background: rgba(0, 255, 0, 0.1);
        border: 1px solid var(--neon-green);
        color: var(--neon-green);
    }
    
    .stWarning {
        background: rgba(255, 165, 0, 0.1);
        border: 1px solid orange;
        color: orange;
    }
    
    /* Loading animation */
    .stSpinner > div {
        border-top-color: var(--neon-cyan) !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: rgba(255, 0, 255, 0.1);
        border: 1px solid var(--neon-purple);
        border-radius: 5px;
    }
    
    /* Number inputs */
    .stNumberInput > div > div > input {
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid var(--neon-cyan);
        color: var(--neon-cyan);
    }
</style>
""", unsafe_allow_html=True)

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

def delete_food_log_entry(entry_id):
    """Delete a specific food log entry by ID."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM food_log WHERE id=?', (entry_id,))
        conn.commit()

def get_last_n_days_log(n):
    today = datetime.date.today()
    days = [(today - datetime.timedelta(days=i)).isoformat() for i in range(n)]
    placeholders = ','.join(['?'] * n)
    query = f"SELECT * FROM food_log WHERE date IN ({placeholders}) ORDER BY date DESC"
    with sqlite3.connect(DB_NAME) as conn:
        df_log = pd.read_sql_query(query, conn, params=days)
    return df_log

# === PASSWORD PROTECTION ===
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        correct_password = st.secrets["PASSWORD"]

        if st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for password.
        st.markdown("""
            <h1 style='text-align: center; color: var(--neon-cyan); text-shadow: 0 0 20px var(--neon-cyan);'>
                🔐 NUTRITION OS v2.1 - ACCESS PROTOCOL
            </h1>
            <div style='text-align: center; margin: 20px;'>
                <p style='color: var(--neon-green); font-family: "Courier New", monospace;'>
                    ENTER AUTHORIZATION CODE TO PROCEED
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input(
                "AUTHORIZATION CODE", 
                type="password", 
                on_change=password_entered, 
                key="password",
                label_visibility="collapsed"
            )
        
        st.markdown("""
            <div style='text-align: center; margin-top: 20px;'>
                <p style='color: var(--neon-green); font-family: "Courier New", monospace; font-size: 12px;'>
                    SYSTEM STATUS: AWAITING INPUT...
                </p>
            </div>
        """, unsafe_allow_html=True)
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.markdown("""
            <h1 style='text-align: center; color: var(--neon-cyan); text-shadow: 0 0 20px var(--neon-cyan);'>
                🔐 NUTRITION OS v2.1 - ACCESS PROTOCOL
            </h1>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input(
                "AUTHORIZATION CODE", 
                type="password", 
                on_change=password_entered, 
                key="password",
                label_visibility="collapsed"
            )
        
        st.markdown("""
            <div style='text-align: center; margin-top: 20px;'>
                <p style='color: red; font-family: "Courier New", monospace; font-size: 14px;'>
                    ⚠️ ACCESS DENIED - INVALID AUTHORIZATION CODE
                </p>
            </div>
        """, unsafe_allow_html=True)
        return False
    else:
        # Password correct.
        return True

if check_password():
    # === STREAMLIT APP ===
    st.sidebar.markdown("""
        <h2 style='color: var(--neon-cyan); text-shadow: 0 0 10px var(--neon-cyan);'>
            🧭 NAVIGATION MATRIX
        </h2>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.selectbox(
        "SELECT MISSION",
        ["🍽️ NUTRITION SCANNER", "📊 DAILY LOG ANALYSIS", "📈 72-HOUR REVIEW", "📅 TEMPORAL CALENDAR"]
    )

    if page == "🍽️ NUTRITION SCANNER":
        st.markdown("""
            <h1 style='text-align: center; color: var(--neon-cyan); text-shadow: 0 0 20px var(--neon-cyan);'>
                🧬 NUTRITION SCANNER
            </h1>
            <p style='text-align: center; color: var(--neon-purple); font-family: "Courier New", monospace;'>
                SCAN FOOD ITEMS • ANALYZE NUTRITIONAL DATA • LOG CONSUMPTION
            </p>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Creatine section with sci-fi styling
        st.markdown("""
            <h3 style='color: var(--neon-green); text-shadow: 0 0 10px var(--neon-green);'>
                ⚡ CREATINE
            </h3>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            creatine_amount = st.number_input("CREATINE DOSAGE (g)", min_value=0, value=0, step=1)
        with col2:
            st.write("")
            st.write("")
            if st.button("⚡ ACTIVATE BOOST", type="primary"):
                if creatine_amount > 0:
                    entry = (
                        today_str,
                        "Creatine",
                        creatine_amount,
                        "Creatine (g)",
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, creatine_amount
                    )
                    add_food_log_entry(entry)
                    st.success(f"✅ CREATINE BOOST ACTIVATED: {creatine_amount}g LOGGED")
                else:
                    st.warning("⚠️ INVALID DOSAGE - ENTER POSITIVE VALUE")

        st.markdown("---")
        
        # Search section
        st.markdown("""
            <h3 style='color: var(--neon-purple); text-shadow: 0 0 10px var(--neon-purple);'>
                🔍 FOOD DATABASE SCAN
            </h3>
        """, unsafe_allow_html=True)
        
        search = st.text_input("ENTER FOOD DESIGNATION", "")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            amount_type = st.radio("INPUT MODE", ["Servings", "Grams"], horizontal=True)
        with col2:
            amount = st.number_input(
                "QUANTITY" if amount_type == "Servings" else "MASS (g)",
                min_value=1, value=1 if amount_type == "Servings" else 100, step=1
            )

        df = load_data(amount_type)

        if search:
            results = df[df["Dish Name"].str.contains(search, case=False, na=False)]
            if not results.empty:
                st.success(f"🎯 TARGET ACQUIRED: {len(results)} MATCH(ES) FOUND")
                
                for idx, row in results.iterrows():
                    st.markdown(f"""
                        <div style='border: 1px solid var(--neon-cyan); border-radius: 10px; padding: 15px; margin: 10px 0; background: rgba(0, 255, 255, 0.1);'>
                            <h3 style='color: var(--neon-purple); text-shadow: 0 0 5px var(--neon-purple);'>{row["Dish Name"]}</h3>
                    """, unsafe_allow_html=True)
                    
                    custom_override = get_custom_grams_nutrition(row["Dish Name"]) if amount_type == "Grams" else None
                    per100g = {col: row[col] for col in NUTRITION_COLS}
                    if custom_override is not None:
                        custom_vals = list(custom_override.values())[1:]
                        for i, col in enumerate(NUTRITION_COLS):
                            per100g[col] = custom_vals[i] if custom_vals[i] is not None else per100g[col]
                        st.info("⚠️ CUSTOMIZED GRAMS NUTRITION VALUES DETECTED")

                    if amount_type == "Servings":
                        scale = amount
                        label = f"servings ({amount})"
                        nutrition = {col: row[col] * scale for col in NUTRITION_COLS}
                    else:
                        scale = amount / 100
                        label = f"{amount}g"
                        nutrition = {col: per100g[col] * scale for col in NUTRITION_COLS}

                    # Ensure all values are scalar before rounding
                    nutrition_display = {}
                    for col, val in nutrition.items():
                        if hasattr(val, 'item'):  # Handle numpy scalars
                            val = val.item()
                        elif hasattr(val, 'values'):  # Handle pandas Series
                            val = float(val.iloc[0]) if len(val) > 0 else 0.0
                        else:
                            try:
                                val = float(val) if val is not None else 0.0
                            except ValueError:
                                # Handle malformed float strings like '2.02.0'
                                val = 0.0
                        nutrition_display[col] = round(val, 2)
                    st.write(nutrition_display)

                    if amount_type == "Grams":
                        with st.expander("EDIT/CORRECT NUTRITION (PER 100G)", expanded=False):
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
                                try:
                                    edit_cols.append(st.number_input(
                                        f"{col} per 100g", value=float(vals[col]), key=f"{col}_{row['Dish Name']}"
                                    ))
                                except ValueError:
                                    edit_cols.append(st.number_input(
                                        f"{col} per 100g", value=0.0, key=f"{col}_{row['Dish Name']}"
                                    ))

                            if st.button("SAVE/CORRECT VALUES (GRAMS ONLY)", key=f"edit_{row['Dish Name']}"):
                                add_custom_grams_nutrition(row["Dish Name"], dict(zip(NUTRITION_COLS[:-1], edit_cols)))
                                st.success("✅ CUSTOM PER-100G VALUES SAVED")

                    if st.button(f"ADD TO TODAY'S LOG: {row['Dish Name']} ({label})", key=f"add_{idx}_{amount}_{amount_type}"):
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
                        st.success(f"✅ {row['Dish Name']} ({label}) ADDED TO LOG")
            else:
                st.warning("⚠️ NO MATCH FOUND")
        else:
            st.info("ENTER A FOOD DESIGNATION ABOVE TO SCAN NUTRITION DATA")

        with st.expander("VIEW ALL FOODS IN DATABASE"):
            st.dataframe(df)

    elif page == "📊 DAILY LOG ANALYSIS":
        st.markdown("""
            <h1 style='text-align: center; color: var(--neon-cyan); text-shadow: 0 0 20px var(--neon-cyan);'>
                📅 DAILY LOG ANALYSIS
            </h1>
        """, unsafe_allow_html=True)
        
        # Initialize session state for goals
        if 'calorie_goal' not in st.session_state:
            st.session_state.calorie_goal = 1500
        if 'protein_goal' not in st.session_state:
            st.session_state.protein_goal = 50
            
        # Goal setting section
        st.markdown("### 🎯 NUTRITION TARGETS")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            new_calorie_goal = st.number_input(
                "DAILY CALORIE TARGET (kcal)",
                min_value=500,
                max_value=5000,
                value=st.session_state.calorie_goal,
                key="calorie_input"
            )
        with col2:
            new_protein_goal = st.number_input(
                "DAILY PROTEIN TARGET (g)",
                min_value=10,
                max_value=300,
                value=st.session_state.protein_goal,
                key="protein_input"
            )
        with col3:
            st.write("")
            st.write("")
            if st.button("⚡ UPDATE TARGETS", type="primary"):
                st.session_state.calorie_goal = new_calorie_goal
                st.session_state.protein_goal = new_protein_goal
                st.success("✅ TARGETS UPDATED")
                st.rerun()
        
        log = get_today_log(today_str)
        if log.empty:
            st.info("⚠️ NO FOODS LOGGED TODAY")
            
            # Show empty pie charts with goals
            st.markdown("### 📈 TARGET VISUALIZATION")
            col1, col2 = st.columns(2)
            
            with col1:
                # Empty calories pie chart
                fig_calories = go.Figure(data=[go.Pie(
                    labels=['Target', 'Not Logged'],
                    values=[st.session_state.calorie_goal, 0],
                    hole=0.4,
                    marker_colors=['#00ffff', '#1a1a2e']
                )])
                fig_calories.update_layout(
                    title=f"CALORIE TARGET: {st.session_state.calorie_goal} kcal",
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#00ffff', family='Courier New'),
                    title_font=dict(size=16, color='#00ffff')
                )
                st.plotly_chart(fig_calories, use_container_width=True)
            
            with col2:
                # Empty protein pie chart
                fig_protein = go.Figure(data=[go.Pie(
                    labels=['Target', 'Not Logged'],
                    values=[st.session_state.protein_goal, 0],
                    hole=0.4,
                    marker_colors=["#ffffff", '#1a1a2e']
                )])
                fig_protein.update_layout(
                    title=f"PROTEIN TARGET: {st.session_state.protein_goal}g",
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#FFFFFF", family='Courier New'),
                    title_font=dict(size=16, color="#ffffff")
                )
                st.plotly_chart(fig_protein, use_container_width=True)
        else:
            st.markdown("#### TODAY'S FOOD LOG")
            display_df = log.copy()
            for idx, row in display_df.iterrows():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.markdown(f"**{row['dish_name']}**")
                with col2:
                    st.markdown(f"{row['amount']} {row['amount_unit']}")
                with col3:
                    st.markdown(f"{row['calories']:.1f} kcal")
                with col4:
                    if st.button("🗑️", key=f"delete_{row['id']}", help=f"Remove {row['dish_name']}"):
                        delete_food_log_entry(row['id'])
                        st.success(f"✅ REMOVED {row['dish_name']} FROM LOG")
                        st.rerun()
            st.markdown("---")
            
            # Fix for TypeError: ensure all values are numeric before summing
            numeric_cols = [col for col in log.columns if col not in ["id", "date", "dish_name", "amount", "amount_unit"]]
            totals = log[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0.0).sum()
            
            # Calculate remaining values
            remaining_calories = max(0, st.session_state.calorie_goal - totals['calories'])
            remaining_protein = max(0, st.session_state.protein_goal - totals['protein'])
            
            # Display metrics with remaining
            st.markdown("#### 📊 NUTRITION ANALYSIS")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Calories", f"{totals['calories']:.1f} kcal", 
                         delta=f"{remaining_calories:.1f} remaining")
            with col2:
                st.metric("Protein", f"{totals['protein']:.1f}g", 
                         delta=f"{remaining_protein:.1f}g remaining")
            with col3:
                st.metric("Carbs", f"{totals['carbohydrates']:.1f}g")
            with col4:
                st.metric("Fats", f"{totals['fats']:.1f}g")
            
            # Pie charts section
            st.markdown("### 📈 VISUAL NUTRITION TRACKING")
            col1, col2 = st.columns(2)
            
            with col1:
                # Calories pie chart
                calories_data = {
                    'Status': ['Consumed', 'Remaining'],
                    'Values': [totals['calories'], remaining_calories]
                }
                fig_calories = go.Figure(data=[go.Pie(
                    labels=calories_data['Status'],
                    values=calories_data['Values'],
                    hole=0.4,
                    marker_colors=['#00ffff', '#1a1a2e'],
                    textinfo='label+percent+value',
                    texttemplate='%{label}<br>%{value:.0f} kcal<br>(%{percent})',
                    textfont=dict(color='#ffffff', family='Courier New')
                )])
                fig_calories.update_layout(
                    title=f"CALORIE PROGRESS<br>Target: {st.session_state.calorie_goal} kcal",
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#00ffff', family='Courier New'),
                    title_font=dict(size=16, color='#00ffff')
                )
                st.plotly_chart(fig_calories, use_container_width=True)
            
            with col2:
                # Protein pie chart
                protein_data = {
                    'Status': ['Consumed', 'Remaining'],
                    'Values': [totals['protein'], remaining_protein]
                }
                fig_protein = go.Figure(data=[go.Pie(
                    labels=protein_data['Status'],
                    values=protein_data['Values'],
                    hole=0.4,
                    marker_colors=["#a1e717", '#1a1a2e'],
                    textinfo='label+percent+value',
                    texttemplate='%{label}<br>%{value:.0f}g<br>(%{percent})',
                    textfont=dict(color='#ffffff', family='Courier New')
                )])
                fig_protein.update_layout(
                    title=f"PROTEIN PROGRESS<br>Target: {st.session_state.protein_goal}g",
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#25e51e", family='Courier New'),
                    title_font=dict(size=16, color="#14a617")
                )
                st.plotly_chart(fig_protein, use_container_width=True)
            
            # Progress bars
            st.markdown("### 📊 PROGRESS INDICATORS")
            calorie_progress = min(100, (totals['calories'] / st.session_state.calorie_goal) * 100)
            protein_progress = min(100, (totals['protein'] / st.session_state.protein_goal) * 100)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**CALORIE PROGRESS: {calorie_progress:.1f}%**")
                st.progress(calorie_progress / 100)
            with col2:
                st.markdown(f"**PROTEIN PROGRESS: {protein_progress:.1f}%**")
                st.progress(protein_progress / 100)
            
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Fiber", f"{totals['fibre']:.1f}g")
            with col2:
                st.metric("Sugar", f"{totals['free_sugar']:.1f}g")
            with col3:
                st.metric("Sodium", f"{totals['sodium']:.0f}mg")
            with col4:
                st.metric("Iron", f"{totals['iron']:.1f}mg")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Creatine", f"{totals['creatine']:.1f}g")
            with col2:
                st.metric("Calcium", f"{totals['calcium']:.0f}mg")
            with col3:
                st.metric("Vitamin C", f"{totals['vitamin_c']:.0f}mg")
            with col4:
                st.metric("Folate", f"{totals['folate']:.0f}µg")
            st.markdown("---")
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("CLEAR ENTIRE LOG FOR TODAY", type="secondary"):
                    clear_today_log(today_str)
                    st.success("✅ TODAY'S LOG CLEARED - PLEASE REFRESH")
                    st.experimental_rerun()

    elif page == "📈 72-HOUR REVIEW":
        st.markdown("""
            <h1 style='text-align: center; color: var(--neon-cyan); text-shadow: 0 0 20px var(--neon-cyan);'>
                📈 72-HOUR REVIEW
            </h1>
        """, unsafe_allow_html=True)
        log = get_last_n_days_log(3)
        if log.empty:
            st.info("⚠️ NO FOOD LOGS FOR PAST 3 DAYS")
        else:
            log['date'] = pd.to_datetime(log['date']).dt.date
            grouped = log.groupby('date')
            for day, df_day in grouped:
                st.markdown(f"### {day}")
                st.dataframe(df_day)
            # Fix for TypeError: ensure all values are numeric before summing
            numeric_cols = [col for col in df_day.columns if col not in ["id", "date", "dish_name", "amount", "amount_unit"]]
            totals = df_day[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0.0).sum()
            st.markdown("**NUTRITION TOTALS:**")
            st.write({col: round(val, 2) for col, val in totals.items()})

    elif page == "📅 TEMPORAL CALENDAR":
        st.markdown("""
            <h1 style='text-align: center; color: var(--neon-cyan); text-shadow: 0 0 20px var(--neon-cyan);'>
                📅 TEMPORAL CALENDAR
            </h1>
        """, unsafe_allow_html=True)
        today = datetime.date.today()
        year = st.sidebar.number_input("YEAR", min_value=1500, max_value=2100, value=today.year)
        month = st.sidebar.number_input("MONTH", min_value=1, max_value=12, value=today.month)

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
            st.info("⚠️ NO FOOD LOGS FOUND FOR THIS MONTH")
        else:
            df_month['date'] = pd.to_datetime(df_month['date']).dt.date
            db_nutrition_cols = [
                "calories", "carbohydrates", "protein", "fats",
                "free_sugar", "fibre", "sodium", "calcium",
                "iron", "vitamin_c", "folate"
            ]
            
            # Fix data types before groupby operation to prevent TypeError
            for col in db_nutrition_cols:
                df_month[col] = pd.to_numeric(df_month[col], errors='coerce').fillna(0.0)
            
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
                            week_data.append(f"{day.day}\nNO DATA")
                    else:
                        week_data.append("")
                cal_data.append(week_data)
            df_cal = pd.DataFrame(cal_data, columns=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
            st.table(df_cal)
