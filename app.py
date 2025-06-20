import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

# --- Set page config (must be first Streamlit command) ---
st.set_page_config(layout="wide", page_title="Retail Sales Dashboard")

# --- Load the cleaned dataset ---
@st.cache_data
def load_data():
    df = pd.read_csv('merged_data.csv', parse_dates=['Date'])
    return df

df = load_data()

# -----------------------------
# Sidebar: Logo and Filters
# -----------------------------
st.sidebar.image("logo.png", use_container_width=True)

st.sidebar.markdown("## 🔍 Filter Options")

# Sidebar filters
date_range = st.sidebar.date_input(
    "📅 Select Date Range",
    value=[df['Date'].min(), df['Date'].max()],
    min_value=df['Date'].min(),
    max_value=df['Date'].max()
)

holiday_filter = st.sidebar.selectbox(
    "🎉 Holiday Weeks Only?",
    options=["All", "Yes", "No"]
)

# Filter dataframe
df_filtered = df.copy()

# Date range filter
df_filtered = df_filtered[
    (df_filtered['Date'] >= pd.to_datetime(date_range[0])) &
    (df_filtered['Date'] <= pd.to_datetime(date_range[1]))
]

# Holiday filter
if holiday_filter == "Yes":
    df_filtered = df_filtered[df_filtered['IsHoliday_x'] == True]
elif holiday_filter == "No":
    df_filtered = df_filtered[df_filtered['IsHoliday_x'] == False]



# --- Main Title and Intro ---
st.title("🛍️ Retail Sales Insights Portal")
st.markdown("""
Welcome to the **Retail Sales Insights Portal**, your data-powered lens into business performance.  
Navigate through key trends, uncover seasonal patterns, and explore forecasting—all in one place. Use the sidebar to select year(s) and dive into tailored analytics built to inform your next big decision.  
""")

# ----------------------------------
# Custom CSS for styling
# ----------------------------------
def stat_card(title, value, icon=None, color="black"):
    icon_html = f"{icon} " if icon else ""
    st.markdown(f"""
        <div style="
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
            height: 150px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <h4 style="color: {color}; margin-bottom: 10px;">{icon_html}{title}</h4>
            <h2 style="margin: 0; font-size: 28px;">{value}</h2>
        </div>
    """, unsafe_allow_html=True)

# ----------------------------------
# Main Content with Tabs
# ----------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Overview",
    "🏬 Store Sales Performance",
    "🎉 Holiday Impact",
    "🔮 Forecast (Coming Soon)"
])

with tab1:
    st.header("📍 Overview")
    st.markdown("High-level summary of sales trends for the selected store and department.")

    # KPI values
    total_sales = f"${df_filtered['Weekly_Sales'].sum():,.2f}"
    avg_sales = f"${df_filtered['Weekly_Sales'].mean():,.2f}"
    max_sales = f"${df_filtered['Weekly_Sales'].max():,.2f}"

    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        stat_card("Total Sales", total_sales, icon="💰", color="green")
    with kpi2:
        stat_card("Average Weekly Sales", avg_sales, icon="📊", color="blue")
    with kpi3:
        stat_card("Max Weekly Sale", max_sales, icon="📈", color="orange")
    
    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("✅ **Insight:** This gives a snapshot of revenue performance. Large gaps between average and max sales may indicate promotional spikes or holiday effects.")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Weekly Sales Line Chart
    st.markdown("#### 📈 Weekly Sales Over Time")
    # Weekly Sales Chart filter controls
    col1, col2 = st.columns(2)
    with col1:
        store_for_chart = st.selectbox(
            "🏪 Select Store for Weekly Sales Chart",
            options=sorted(df['Store'].unique())
        )
    with col2:
        dept_for_chart = st.selectbox(
            "📦 Select Department for Weekly Sales Chart",
            options=sorted(df['Dept'].unique())
        )

    # Filter df for weekly sales chart based on above selects + date range + holiday filter (optional)
    df_chart_filtered = df[
        (df['Store'] == store_for_chart) &
        (df['Dept'] == dept_for_chart) &
        (df['Date'] >= pd.to_datetime(date_range[0])) &
        (df['Date'] <= pd.to_datetime(date_range[1]))
    ]
    if holiday_filter == "Yes":
        df_chart_filtered = df_chart_filtered[df_chart_filtered['IsHoliday_x'] == True]
    elif holiday_filter == "No":
        df_chart_filtered = df_chart_filtered[df_chart_filtered['IsHoliday_x'] == False]

    # Weekly Sales Line Chart
    fig_weekly = px.line(
        df_chart_filtered.sort_values('Date'),
        x='Date',
        y='Weekly_Sales',
        title=f"Weekly Sales Over Time for Store {store_for_chart}, Dept {dept_for_chart}",
        labels={"Weekly_Sales": "Weekly Sales", "Date": "Date"},
        markers=True
    )
    st.plotly_chart(fig_weekly, use_container_width=True)
    st.markdown("✅ **Insight:** Look for trends, spikes or drops which might correspond to marketing campaigns, holidays or other events.")

    st.markdown("<br><br>", unsafe_allow_html=True)
    # Monthly Sales Bar Chart
    st.markdown("#### 📅 Total Sales by Month")
    monthly_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    monthly_sales = (
        df_filtered.groupby('Month_Name')['Weekly_Sales']
        .sum()
        .reindex(monthly_order)
        .reset_index()
        .rename(columns={'Month_Name': 'Month', 'Weekly_Sales': 'Sales'})
    )
    fig_monthly = px.bar(
        monthly_sales,
        x='Month',
        y='Sales',
        color='Month',
        color_discrete_sequence=px.colors.qualitative.Safe,
        title="Total Sales by Month"
    )
    fig_monthly.update_layout(
        xaxis=dict(categoryorder='array', categoryarray=monthly_order),
        yaxis_title="Total Sales",
        showlegend=False
    )
    st.plotly_chart(fig_monthly, use_container_width=True)
    st.markdown("✅ **Insight:** Identify your peak sales months to optimize inventory and promotions.")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("#### 📊 Sales by Week Number")
    week_sales = (
        df_filtered.groupby('Week')['Weekly_Sales']
        .sum()
        .reset_index()
        .rename(columns={'Week': 'Week_Number', 'Weekly_Sales': 'Sales'})
    )
    fig_week = px.bar(
        week_sales,
        x='Week_Number',
        y='Sales',
        title="Sales by Week Number",
        color='Sales',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig_week.update_layout(yaxis_title="Total Sales", xaxis_title="Week Number", showlegend=False)
    st.plotly_chart(fig_week, use_container_width=True)
    st.markdown("✅ **Insight:** Shows how sales vary across weeks of the year.")

with tab2:
    st.header("🏬 Store Sales Performance")
    st.markdown("Analyze sales performance across stores and departments with meaningful comparisons.")

    # --- Monthly Sales Trend (Overall, no store/dept filter) ---
    monthly_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    monthly_sales = (
        df.groupby('Month_Name')['Weekly_Sales']
        .sum()
        .reindex(monthly_order)
        .reset_index()
        .rename(columns={'Month_Name': 'Month', 'Weekly_Sales': 'Sales'})
    )
    fig_monthly_trend = px.line(
        monthly_sales,
        x='Month',
        y='Sales',
        title="📈 Monthly Sales Trend (All Stores & Depts)",
        markers=True,
        labels={"Sales": "Total Sales", "Month": "Month"}
    )
    fig_monthly_trend.update_layout(xaxis=dict(categoryorder='array', categoryarray=monthly_order))
    st.plotly_chart(fig_monthly_trend, use_container_width=True)
    st.markdown("✅ **Insight:** Observe seasonal patterns and sales cycles across the year.")

    st.markdown("---")

    # --- Sales by Store Size (Filtered by Store) ---
    store_for_size = st.selectbox(
        "🏪 Select Store for Store Size Sales Chart",
        options=sorted(df['Store'].unique()),
        key='store_size_filter'
    )
    df_size_filtered = df[df['Store'] == store_for_size]
    if 'Size' in df_size_filtered.columns:
        size_sales = (
            df_size_filtered.groupby('Size')['Weekly_Sales']
            .sum()
            .reset_index()
            .sort_values('Size')
        )
        fig_size = px.bar(
            size_sales,
            x='Size',
            y='Weekly_Sales',
            title=f"🏗️ Sales by Store Size for Store {store_for_size}",
            labels={"Size": "Store Size", "Weekly_Sales": "Total Sales"},
            color='Weekly_Sales',
            color_continuous_scale=px.colors.sequential.Plasma
        )
        st.plotly_chart(fig_size, use_container_width=True)
        st.markdown("✅ **Insight:** Larger store formats may support higher sales volumes.")
    else:
        st.info("Store Size data not available for this selection.")

    st.markdown("---")

    # --- Weekly Sales Distribution (Filtered by Dept) ---
    dept_for_sales = st.selectbox(
        "📦 Select Department for Sales Distribution",
        options=sorted(df['Dept'].unique()),
        key='dept_sales_filter'
    )
    df_dept_filtered = df[df['Dept'] == dept_for_sales]
    fig_hist = px.histogram(
        df_dept_filtered,
        x='Weekly_Sales',
        nbins=30,
        title=f"📊 Weekly Sales Distribution for Department {dept_for_sales}",
        labels={'Weekly_Sales': 'Weekly Sales'}
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown("✅ **Insight:** Understand the sales variability within the selected department.")

    st.markdown("---")

    # --- Top Departments by Sales (Overall) ---
    top_n = st.slider("🎯 Number of Top Departments to Show", 5, 20, 10, key='top_dept_slider')
    dept_sales = (
        df.groupby('Dept')['Weekly_Sales']
        .sum()
        .reset_index()
        .sort_values('Weekly_Sales', ascending=False)
        .head(top_n)
    )
    fig_top_depts = px.bar(
        dept_sales,
        y='Dept',
        x='Weekly_Sales',
        orientation='h',
        title=f"🏆 Top {top_n} Departments by Sales",
        labels={"Dept": "Department", "Weekly_Sales": "Total Sales"},
        color='Weekly_Sales',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig_top_depts.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top_depts, use_container_width=True)
    st.markdown("✅ **Insight:** These departments drive the highest revenue and deserve strategic focus.")

    st.markdown("---")

   # --- Average Sales by Fuel Price Range ---

    fuel_bins = pd.cut(df['Fuel_Price'], bins=5)
    df['Fuel_Bin'] = fuel_bins.astype(str)  # Convert to string for plotting

    fuel_sales = df.groupby('Fuel_Bin')['Weekly_Sales'].mean().reset_index()
    fuel_sales.columns = ['Fuel Price Range', 'Average Weekly Sales']

    fig_fuel_bar = px.bar(
        fuel_sales,
        x='Fuel Price Range',
        y='Average Weekly Sales',
        title="⛽ Average Weekly Sales by Fuel Price Range",
        labels={'Fuel Price Range': 'Fuel Price Range', 'Average Weekly Sales': 'Avg Weekly Sales'},
        color='Average Weekly Sales',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_fuel_bar, use_container_width=True)
    st.markdown("✅ **Insight:** Highlights how average sales vary with fuel prices.")

    st.markdown("---")

    # --- Average Sales by Temperature Range ---

    temp_bins = pd.cut(df['Temperature'], bins=6)
    df['Temp_Bin'] = temp_bins.astype(str)  # Convert to string for plotting

    temp_sales = df.groupby('Temp_Bin')['Weekly_Sales'].mean().reset_index()
    temp_sales.columns = ['Temperature Range', 'Average Weekly Sales']

    fig_temp_bar = px.bar(
        temp_sales,
        x='Temperature Range',
        y='Average Weekly Sales',
        title="🌡️ Average Weekly Sales by Temperature Range",
        labels={'Temperature Range': 'Temperature (°F)', 'Average Weekly Sales': 'Avg Weekly Sales'},
        color='Average Weekly Sales',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_temp_bar, use_container_width=True)
    st.markdown("✅ **Insight:** Understand how average sales behave under different temperature conditions.")


    st.markdown("---")

    # --- Store Type Analysis ---
    if 'Type' in df.columns:
        type_sales = (
            df.groupby('Type')['Weekly_Sales']
            .sum()
            .reset_index()
            .sort_values('Weekly_Sales', ascending=False)
        )
        fig_type = px.bar(
            type_sales,
            x='Type',
            y='Weekly_Sales',
            title="🏢 Total Sales by Store Type",
            labels={'Type': 'Store Type', 'Weekly_Sales': 'Total Sales'},
            color='Weekly_Sales',
            color_continuous_scale=px.colors.sequential.Cividis
        )
        st.plotly_chart(fig_type, use_container_width=True)
        st.markdown("✅ **Insight:** Compares performance between store types")


with tab3:
    st.header("🎉 Holiday Impact")
    st.markdown("Analyze how major U.S. holidays affect weekly retail sales trends.")

    # 1. Holiday vs Non-Holiday Comparison
    st.markdown("### 📊 Average Sales: Holiday vs Non-Holiday Weeks")
    holiday_comparison = df.copy()
    holiday_comparison['Holiday_Flag'] = holiday_comparison['IsHoliday_x'].replace({True: 'Holiday', False: 'Non-Holiday'})
    holiday_avg = (
        holiday_comparison.groupby('Holiday_Flag')['Weekly_Sales']
        .mean()
        .reset_index()
        .rename(columns={'Weekly_Sales': 'Average Sales'})
    )
    fig_holiday_avg = px.bar(
        holiday_avg,
        x='Holiday_Flag',
        y='Average Sales',
        color='Holiday_Flag',
        title="Average Weekly Sales During Holiday vs Non-Holiday Weeks",
        labels={'Holiday_Flag': '', 'Average Sales': 'Avg Weekly Sales'},
        color_discrete_map={'Holiday': 'crimson', 'Non-Holiday': 'royalblue'}
    )
    st.plotly_chart(fig_holiday_avg, use_container_width=True)
    st.markdown("✅ **Insight:** Understand whether holidays drive more sales compared to regular weeks.")

    st.markdown("---")

    # 2. Sales by Specific Holidays
    st.markdown("### 🎯 Sales Comparison by Holiday Type")
    df_holidays = df.copy()
    df_holidays['Holiday_Type'] = 'None'
    df_holidays.loc[df_holidays['IsSuperBowl'], 'Holiday_Type'] = 'Super Bowl'
    df_holidays.loc[df_holidays['IsLaborDay'], 'Holiday_Type'] = 'Labor Day'
    df_holidays.loc[df_holidays['IsThanksgiving'], 'Holiday_Type'] = 'Thanksgiving'
    df_holidays.loc[df_holidays['IsChristmas'], 'Holiday_Type'] = 'Christmas'

    holiday_sales = (
        df_holidays[df_holidays['Holiday_Type'] != 'None']
        .groupby(['Year', 'Holiday_Type'])['Weekly_Sales']
        .sum()
        .reset_index()
    )
    fig_specific = px.bar(
        holiday_sales,
        x='Holiday_Type',
        y='Weekly_Sales',
        color='Year',
        barmode='group',
        title="Total Sales During Specific Holidays by Year",
        labels={'Weekly_Sales': 'Total Sales', 'Holiday_Type': 'Holiday'}
    )
    st.plotly_chart(fig_specific, use_container_width=True)
    st.markdown("✅ **Insight:** Identify which holiday drives the highest sales across years.")

    st.markdown("---")

    # 3. Sales Trends Around Holidays (2 weeks before & after)
    st.markdown("### 📈 Sales Trend: 2 Weeks Before and After Holidays")

    def get_holiday_windows(holiday_dates, name):
        holiday_trend_list = []
        for date in holiday_dates:
            window = df[(df['Date'] >= date - pd.Timedelta(weeks=2)) & (df['Date'] <= date + pd.Timedelta(weeks=2))].copy()
            window['Event'] = name
            window['Delta_Week'] = (window['Date'] - date).dt.days // 7
            holiday_trend_list.append(window)
        return pd.concat(holiday_trend_list)

    combined_trends = pd.concat([
        get_holiday_windows(pd.to_datetime(['2010-02-12', '2011-02-11', '2012-02-10', '2013-02-08']), 'Super Bowl'),
        get_holiday_windows(pd.to_datetime(['2010-09-10', '2011-09-09', '2012-09-07', '2013-09-06']), 'Labor Day'),
        get_holiday_windows(pd.to_datetime(['2010-11-26', '2011-11-25', '2012-11-23', '2013-11-29']), 'Thanksgiving'),
        get_holiday_windows(pd.to_datetime(['2010-12-31', '2011-12-30', '2012-12-28', '2013-12-27']), 'Christmas')
    ])

    trend_chart = combined_trends.groupby(['Delta_Week', 'Event'])['Weekly_Sales'].mean().reset_index()

    fig_trend = px.line(
        trend_chart,
        x='Delta_Week',
        y='Weekly_Sales',
        color='Event',
        markers=True,
        title="Sales Trends Two Weeks Before & After Each Holiday",
        labels={"Delta_Week": "Weeks from Holiday", "Weekly_Sales": "Average Sales"}
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown("✅ **Insight:** Understand sales build-up and drop-off around major holidays.")

    st.markdown("---")

     # Filters for Store and Department
    col1, col2 = st.columns(2)

    with col1:
        store_holiday = st.selectbox(
            "🏪 Select Store",
            options=sorted(df['Store'].unique()),
            key='store_holiday_lift'
        )

    with col2:
        dept_holiday = st.selectbox(
            "📦 Select Department",
            options=sorted(df['Dept'].unique()),
            key='dept_holiday_lift'
        )

    # Filter data by store and dept
    df_filtered = df[(df['Store'] == store_holiday) & (df['Dept'] == dept_holiday)].copy()

    # Create Holiday_Type column based on holiday flags
    def get_holiday_type(row):
        if row.get('IsSuperBowl', False):
            return 'Super Bowl'
        elif row.get('IsLaborDay', False):
            return 'Labor Day'
        elif row.get('IsThanksgiving', False):
            return 'Thanksgiving'
        elif row.get('IsChristmas', False):
            return 'Christmas'
        else:
            return 'None'

    df_filtered['Holiday_Type'] = df_filtered.apply(get_holiday_type, axis=1)

    # Filter out 'None' to compare holidays with non-holiday weeks
    holiday_types = [ht for ht in df_filtered['Holiday_Type'].unique() if ht != 'None']

    results = []

    for ht in holiday_types:
        holiday_sales_avg = df_filtered[df_filtered['Holiday_Type'] == ht]['Weekly_Sales'].mean()
        non_holiday_sales_avg = df_filtered[df_filtered['Holiday_Type'] == 'None']['Weekly_Sales'].mean()

        # Avoid division by zero
        if not non_holiday_sales_avg or pd.isna(non_holiday_sales_avg):
            lift_pct = None
        else:
            lift_pct = ((holiday_sales_avg - non_holiday_sales_avg) / non_holiday_sales_avg) * 100

        results.append({
            "Holiday_Type": ht,
            "Holiday_Week_Avg_Sales": holiday_sales_avg,
            "Non_Holiday_Week_Avg_Sales": non_holiday_sales_avg,
            "Sales_Lift_Percent": lift_pct
        })

    df_lift = pd.DataFrame(results).dropna()

    if df_lift.empty:
        st.info("No holiday data available for this store and department.")
    else:
        df_lift = df_lift.sort_values(by='Sales_Lift_Percent', ascending=False)

        fig_lift = px.bar(
            df_lift,
            x='Holiday_Type',
            y='Sales_Lift_Percent',
            title=f"Sales Lift % During Holidays vs Non-Holiday Weeks for Store {store_holiday}, Dept {dept_holiday}",
            labels={'Sales_Lift_Percent': 'Sales Lift (%)', 'Holiday_Type': 'Holiday'},
            text=df_lift['Sales_Lift_Percent'].apply(lambda x: f"{x:.2f}%")
        )
        fig_lift.update_traces(textposition='outside')
        fig_lift.update_layout(yaxis_title='Sales Lift (%)', xaxis_title='Holiday')
        st.plotly_chart(fig_lift, use_container_width=True)

        with st.expander("See Detailed Numbers"):
            st.dataframe(df_lift.style.format({
                "Holiday_Week_Avg_Sales": "${:,.2f}",
                "Non_Holiday_Week_Avg_Sales": "${:,.2f}",
                "Sales_Lift_Percent": "{:.2f}%"
            }))

with tab4:
    st.header("🔮 Forecast (Coming Soon)")
    st.markdown("""
    🚧 We're working on predictive analytics using advanced forecasting models like machine learning algorithms.

    Stay tuned for future updates! 📈✨
    """)

    
# ========================
# 📌 FOOTER
# ========================
st.markdown("""---""")

footer = """
<style>
/* Hide Streamlit's default footer */
footer {visibility: hidden;}

/* Custom footer style */
.footer-style {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #001f3f;
    color: white;
    text-align: center;
    padding: 10px 0;
    font-size: 14px;
    opacity: 0.9;
    z-index: 1000;
}
</style>

<div class="footer-style">
    © 2025 DTG Labs — All rights reserved.
</div>
"""

st.markdown(footer, unsafe_allow_html=True)