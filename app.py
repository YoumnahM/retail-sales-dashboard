import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# --- Set page config (must be first Streamlit command) ---
st.set_page_config(layout="wide", page_title="Retail Sales Dashboard")

# --- Sidebar Header ---
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.markdown("## 🧭 Dashboard Filters")
st.sidebar.markdown("Use the filters below to explore your business performance.")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("merged_data.csv", parse_dates=["Date"])
    return df

df = load_data()

# --- Filter: Date Range ---
date_range = st.sidebar.date_input(
    "📅 Select Time Period",
    value=[df["Date"].min(), df["Date"].max()],
    min_value=df["Date"].min(),
    max_value=df["Date"].max()
)

# --- Filter: Holiday Focus ---
holiday_focus = st.sidebar.radio(
    "🎉 Focus on Holiday Weeks?",
    options=["All Weeks", "Holiday Weeks Only", "Non-Holiday Weeks"]
)

# --- Filter: Store Selection with "All" Option ---
store_list = sorted(df['Store_Name'].unique())
store_selection = st.sidebar.selectbox(
    "🏪 Select Store",
    options=["All"] + store_list
)

# --- Filter: Department Selection with "All" Option ---
dept_list = sorted(df['Dept_Name'].unique())
dept_selection = st.sidebar.selectbox(
    "📦 Select Department",
    options=["All"] + dept_list
)

# --- Apply Filters ---
df_filtered = df.copy()

# Date Filter
df_filtered = df_filtered[
    (df_filtered["Date"] >= pd.to_datetime(date_range[0])) &
    (df_filtered["Date"] <= pd.to_datetime(date_range[1]))
]

# Holiday Filter
if holiday_focus == "Holiday Weeks Only":
    df_filtered = df_filtered[df_filtered["IsHoliday_x"] == True]
elif holiday_focus == "Non-Holiday Weeks":
    df_filtered = df_filtered[df_filtered["IsHoliday_x"] == False]

# Store Filter
if store_selection != "All":
    df_filtered = df_filtered[df_filtered["Store_Name"] == store_selection]

# Department Filter
if dept_selection != "All":
    df_filtered = df_filtered[df_filtered["Dept_Name"] == dept_selection]



# --- Page Title and Introduction ---
st.title("🛍️ Retail Business Performance Dashboard")
st.markdown("""
Welcome to your all-in-one dashboard for tracking retail sales performance, trends, and business insights.
            
This tool is designed to help decision-makers understand what’s working, spot areas of concern, and drive data-backed strategies.
Use the filters on the left to tailor the data to specific time periods or holiday activity.
""")

# ----------------------------------
# Custom CSS for styling
# ----------------------------------


# --- Tabs Layout ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive Summary",
    "📈 Performance Drivers",
    "🔍 Opportunity Finder",
    "🔮 Forecast (Coming Soon)"
])

# =======================
# 📊 Executive Summary
# =======================
with tab1:
    st.subheader("📊 Executive Summary")
    st.markdown("Get a bird’s-eye view of your business performance. This tab summarizes key sales indicators to help you monitor growth, spot trends, and guide strategic decisions.")

    # --- KPI Calculations ---
    total_sales_val = df_filtered['Weekly_Sales'].sum()
    avg_sales_val = df_filtered['Weekly_Sales'].mean()
    max_sales_val = df_filtered['Weekly_Sales'].max()

    # --- KPI Card Function ---
    def kpi_card(title, value, icon, bg_color, text_color):
        return f"""
        <div style="background-color: {bg_color}; padding: 25px; border-radius: 15px;
                    text-align: center; width: 100%; height: 215px;
                    display: flex; flex-direction: column; justify-content: center;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <div style="font-size: 36px; margin-bottom: 8px;">{icon}</div>
            <h3 style="color: {text_color}; margin: 0;">{title}</h3>
            <h2 style="color: {text_color}; margin-top: 5px;">{value}</h2>
        </div>
        """

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(kpi_card("Total Sales", f"${total_sales_val:,.0f}", "💰", "#d4f1e4", "#136953"), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_card("Avg Weekly Sales", f"${avg_sales_val:,.0f}", "📊", "#dbe7ff", "#003d99"), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_card("Max Weekly Sale", f"${max_sales_val:,.0f}", "📈", "#ffe5d9", "#b34700"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Best & Worst Month ---
    monthly_sales = df_filtered.groupby('Month_Name')['Weekly_Sales'].sum()
    best_month = monthly_sales.idxmax()
    best_month_sales = monthly_sales.max()
    worst_month = monthly_sales.idxmin()
    worst_month_sales = monthly_sales.min()

    col4, col5 = st.columns([1, 2])
    with col4:
        st.markdown(f"""
        <div style='background-color:#fff7e6; padding:20px; border-radius:12px; text-align:center;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.1);'>
            <h3 style='color:#b37400;'>🌟 Best Month</h3>
            <h2 style='color:#996d00;'>{best_month}</h2>
            <p style='color:#b38f00;'>${best_month_sales:,.0f} in sales</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div style='background-color:#fff0f5; padding:20px; border-radius:12px; text-align:center;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.1);'>
            <h3 style='color:#cc3399;'>🔻 Lowest Month</h3>
            <h2 style='color:#a30073;'>{worst_month}</h2>
            <p style='color:#cc6699;'>${worst_month_sales:,.0f} in sales</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

   # --- Holiday Impact ---
    holiday_sales = df_filtered[df_filtered['IsHoliday_x'] == True]['Weekly_Sales'].mean()
    non_holiday_sales = df_filtered[df_filtered['IsHoliday_x'] == False]['Weekly_Sales'].mean()

    uplift_pct = 0
    if non_holiday_sales > 0:
        uplift_pct = ((holiday_sales - non_holiday_sales) / non_holiday_sales) * 100

    if uplift_pct > 0:
        holiday_message = f"🎉 Holiday weeks show an uplift of  <b>{uplift_pct:.1f}%</b>  compared to non-holiday weeks."
    else:
        holiday_message = "Holiday weeks have similar or slightly lower sales than regular weeks."

    st.markdown(f"""
    <div style='background-color:#f0f8ff; padding:20px; border-radius:12px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);'>
        <h3 style='color:#007acc;'>🎊 Holiday Performance</h3>
        <p style='font-size:16px;'>{holiday_message}</p>
    </div>
    """, unsafe_allow_html=True)


    st.markdown("<br>", unsafe_allow_html=True)

    # --- Monthly Sales Trend (YoY) ---
    st.markdown("### 📈 Monthly Sales Trend (Year-over-Year)")
    monthly_trend = df_filtered.groupby(['Year', 'Month', 'Month_Name'])['Weekly_Sales'].sum().reset_index()

    # Ensure correct order
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_trend['Month_Name'] = pd.Categorical(monthly_trend['Month_Name'], categories=month_order, ordered=True)
    monthly_trend.sort_values(['Year', 'Month'], inplace=True)

    fig_month_trend = px.line(
        monthly_trend,
        x='Month',
        y='Weekly_Sales',
        color='Year',
        markers=True,
        labels={'Weekly_Sales': 'Total Sales', 'Month': 'Month'},
        category_orders={'Month': list(range(1, 13))}
    )
    fig_month_trend.update_layout(
        xaxis=dict(tickmode='array', tickvals=list(range(1, 13)), ticktext=month_order)
    )
    st.plotly_chart(fig_month_trend, use_container_width=True)

    st.info("""
    📌 **Insight:**  
    This year-over-year view highlights recurring seasonal spikes or dips.  
    Use this to plan campaigns, align inventory cycles, or compare performance against historical benchmarks.
    """)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- Weekly Sales Trend ---
    st.markdown("### 📆 Weekly Sales Over Time")
    df_trend = df_filtered.groupby("Date")["Weekly_Sales"].sum().reset_index()
    fig_weekly = px.line(
        df_trend,
        x="Date",
        y="Weekly_Sales",
        markers=True,
        labels={"Weekly_Sales": "Total Sales", "Date": "Week"}
    )
    st.plotly_chart(fig_weekly, use_container_width=True)
    st.info("""
    ✅ **Business Insight:**  
    Understand week-to-week sales movement.  
    Spot spikes (e.g. promotions), dips (e.g. inventory issues), or patterns.  
    This is crucial for weekly planning, advertising schedules, and cash flow forecasting.
    """)

        # --- ALERTS SECTION ---
    st.markdown("## 🚨 Key Business Alerts & Signals")

    # --- ALERT: Compare current month sales vs previous year same month ---
    latest_year = df_filtered['Year'].max()
    prev_year = latest_year - 1

    latest_month = df_filtered[df_filtered['Year'] == latest_year]['Month'].max()

    current_period_sales = df_filtered[
        (df_filtered['Year'] == latest_year) & (df_filtered['Month'] == latest_month)
    ]['Weekly_Sales'].sum()

    prev_period_sales = df_filtered[
        (df_filtered['Year'] == prev_year) & (df_filtered['Month'] == latest_month)
    ]['Weekly_Sales'].sum()

    yoy_change = 0
    if prev_period_sales > 0:
        yoy_change = ((current_period_sales - prev_period_sales) / prev_period_sales) * 100

    if yoy_change > 5:
        st.success(f"✅ Sales are up by **{yoy_change:.1f}%** compared to the same month last year.")
    elif yoy_change < -5:
        st.error(f"📉 Sales have dropped by **{abs(yoy_change):.1f}%** compared to the same month last year.")
    else:
        st.warning(f"⚠️ Sales are stable with a slight change of **{yoy_change:.1f}%** year-over-year.")

    # --- ALERT: Top Performing Department ---
    top_dept = df_filtered.groupby('Dept_Name')['Weekly_Sales'].sum().reset_index()\
                .sort_values('Weekly_Sales', ascending=False).iloc[0]
    st.info(f"🏆 **{top_dept['Dept_Name']}** is currently your top-performing department with ${top_dept['Weekly_Sales']:,.0f} in sales.")

    # --- ALERT: Holiday uplift trend ---
    holiday_sales = df_filtered[df_filtered['IsHoliday_x'] == True]['Weekly_Sales'].mean()
    non_holiday_sales = df_filtered[df_filtered['IsHoliday_x'] == False]['Weekly_Sales'].mean()

    if holiday_sales > 0 and non_holiday_sales > 0:
        holiday_uplift_pct = ((holiday_sales - non_holiday_sales) / non_holiday_sales) * 100
        if holiday_uplift_pct > 10:
            st.success(f"🎉 Holiday weeks are generating a strong uplift of **{holiday_uplift_pct:.1f}%** over non-holiday weeks.")
        elif holiday_uplift_pct < 5:
            st.warning("🤔 Holiday uplift is minimal this season. Consider revisiting your promotional strategy.")

    # --- ALERT: Underperforming Store ---
    store_perf = df_filtered.groupby('Store_Name')['Weekly_Sales'].sum().reset_index()
    lowest_store = store_perf.sort_values('Weekly_Sales').iloc[0]
    st.error(f"🚩 **{lowest_store['Store_Name']}** has the lowest sales performance (${lowest_store['Weekly_Sales']:,.0f}). Consider further review.")




with tab2:
    st.subheader("📈 Performance Drivers")
    st.markdown("Understand which factors influence your sales the most — across stores, departments, pricing, and even weather. Use these insights to sharpen your business strategy.")

    # --- 1. Top 5 Performing Stores ---
    top_stores = (
        df_filtered.groupby('Store_Name')['Weekly_Sales']
        .sum()
        .reset_index()
        .sort_values('Weekly_Sales', ascending=False)
        .head(5)
    )
    fig_top_stores = px.bar(
        top_stores,
        x='Store_Name',
        y='Weekly_Sales',
        title="🏪 Top 5 Performing Stores",
        labels={"Store_Name": "Store", "Weekly_Sales": "Total Sales"},
        color='Weekly_Sales',
        color_continuous_scale='greens'
    )
    st.plotly_chart(fig_top_stores, use_container_width=True)
    st.info("""
    🔍 **Business Insight:**  
    These stores are your top revenue contributors. Consider replicating their model — promotions, layout, staff training — across other stores to lift overall performance.
    """)

    # --- 2. Top 5 Performing Departments ---
    top_depts = (
        df_filtered.groupby('Dept_Name')['Weekly_Sales']
        .sum()
        .reset_index()
        .sort_values('Weekly_Sales', ascending=False)
        .head(5)
    )
    fig_top_depts = px.bar(
        top_depts,
        x='Dept_Name',
        y='Weekly_Sales',
        title="📦 Top 5 Performing Departments",
        labels={"Dept_Name": "Department", "Weekly_Sales": "Total Sales"},
        color='Weekly_Sales',
        color_continuous_scale='blues'
    )
    st.plotly_chart(fig_top_depts, use_container_width=True)
    st.info("""
    🔍 **Business Insight:**  
    Your best-performing departments drive core revenue. Use this insight to double down on inventory, marketing, and seasonal campaigns for these categories.
    """)

    st.markdown("---")

    # --- 3. Store Size Impact ---
    if 'Size' in df.columns:
        bins = [0, 10000, 30000, 60000, 100000, df['Size'].max() + 1]
        labels = ['Very Small', 'Small', 'Medium', 'Large', 'Very Large']
        df_filtered['Size_Category'] = pd.cut(df_filtered['Size'], bins=bins, labels=labels, right=False)

        size_cat_avg_sales = df_filtered.groupby('Size_Category')['Weekly_Sales'].mean().reset_index()
        fig_size_cat = px.bar(
            size_cat_avg_sales,
            x='Size_Category',
            y='Weekly_Sales',
            title="🏗️ Avg Weekly Sales by Store Size Category",
            labels={"Size_Category": "Store Size", "Weekly_Sales": "Avg Weekly Sales"},
            color='Weekly_Sales',
            color_continuous_scale='plasma'
        )
        st.plotly_chart(fig_size_cat, use_container_width=True)
        st.info("""
        🔍 **Business Insight:**  
        Larger stores often yield more sales due to wider assortments. But if small stores perform competitively, they may offer higher ROI per sq ft. Consider this when scaling or renovating locations.
        """)

    # --- 4. Store Type Influence ---
    if 'Type' in df_filtered.columns:
        type_sales = df_filtered.groupby('Type')['Weekly_Sales'].sum().reset_index().sort_values('Weekly_Sales', ascending=False)
        fig_type = px.bar(
            type_sales,
            x='Type',
            y='Weekly_Sales',
            title="🏢 Total Sales by Store Type",
            labels={'Type': 'Store Type', 'Weekly_Sales': 'Total Sales'},
            color='Weekly_Sales',
            color_continuous_scale='cividis'
        )
        st.plotly_chart(fig_type, use_container_width=True)
        st.info("""
        🔍 **Business Insight:**  
        Not all store types perform equally. Focus on expanding store types with strong sales and reevaluate those underperforming for possible rebranding or optimization.
        """)

    st.markdown("---")

    # --- 5. Total Sales by Month ---
    monthly_sales = df_filtered.groupby('Month_Name')['Weekly_Sales'].sum().reset_index()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_sales['Month_Name'] = pd.Categorical(monthly_sales['Month_Name'], categories=month_order, ordered=True)
    monthly_sales.sort_values('Month_Name', inplace=True)

    fig_month_sales = px.bar(
        monthly_sales,
        x='Month_Name',
        y='Weekly_Sales',
        title="🗓️ Total Sales by Month",
        labels={"Month_Name": "Month", "Weekly_Sales": "Total Sales"},
        color='Weekly_Sales',
        color_continuous_scale='purples'
    )
    st.plotly_chart(fig_month_sales, use_container_width=True)
    st.info("""
    🔍 **Business Insight:**  
    Use this to detect high and low seasons. Plan big promotions and inventory spikes in peak months to maximize revenue and footfall.
    """)

    st.markdown("---")

    # --- 6. Fuel Price Effect ---
    fuel_bins = pd.cut(df_filtered['Fuel_Price'], bins=5)
    df_filtered['Fuel_Bin'] = fuel_bins.astype(str)
    fuel_sales = df_filtered.groupby('Fuel_Bin')['Weekly_Sales'].mean().reset_index()
    fuel_sales.columns = ['Fuel Price Range', 'Average Weekly Sales']

    fig_fuel = px.bar(
        fuel_sales,
        x='Fuel Price Range',
        y='Average Weekly Sales',
        title="⛽ Avg Weekly Sales by Fuel Price Range",
        labels={'Fuel Price Range': 'Fuel Price Range', 'Average Weekly Sales': 'Avg Weekly Sales'},
        color='Average Weekly Sales',
        color_continuous_scale='blues'
    )
    st.plotly_chart(fig_fuel, use_container_width=True)
    st.info("""
    🔍 **Business Insight:**  
    High fuel prices may keep customers at home. Watch for dips and shift strategy — like boosting online promos or click-and-collect.
    """)

    st.markdown("---")

    # --- 7. Temperature Impact ---
    temp_bins = pd.cut(df_filtered['Temperature'], bins=6)
    df_filtered['Temp_Bin'] = temp_bins.astype(str)
    temp_sales = df_filtered.groupby('Temp_Bin')['Weekly_Sales'].mean().reset_index()
    temp_sales.columns = ['Temperature Range', 'Average Weekly Sales']

    fig_temp = px.bar(
        temp_sales,
        x='Temperature Range',
        y='Average Weekly Sales',
        title="🌡️ Avg Weekly Sales by Temperature",
        labels={'Temperature Range': 'Temperature (°F)', 'Average Weekly Sales': 'Avg Weekly Sales'},
        color='Average Weekly Sales',
        color_continuous_scale='reds'
    )
    st.plotly_chart(fig_temp, use_container_width=True)
    st.info("""
    🔍 **Business Insight:**  
    Certain products or store visits rise with temperature. Use weather trends to plan seasonal inventory and marketing campaigns.
    """)



with tab3:
    st.subheader("🔍 Opportunity Finder")
    st.markdown("Identify hidden opportunities, address underperformance, and leverage strategic timing to drive growth.")

# --- 1. Top 10 Departments by Sales ---
    st.markdown("### 🏆 Top 10 Departments by Total Sales")

    top10_dept_sales = (
        df_filtered.groupby('Dept_Name')['Weekly_Sales']
        .sum()
        .reset_index()
        .sort_values('Weekly_Sales', ascending=False)
        .head(10)
    )

    fig_top10 = px.bar(
        top10_dept_sales,
        x='Weekly_Sales',
        y='Dept_Name',
        orientation='h',
        title="Top 10 Revenue-Contributing Departments",
        labels={'Dept_Name': 'Department', 'Weekly_Sales': 'Total Sales'},
        color='Weekly_Sales',
        color_continuous_scale='Blues'
    )
    fig_top10.update_layout(yaxis=dict(categoryorder='total ascending'))

    st.plotly_chart(fig_top10, use_container_width=True)

    st.info("🔍 **Insight:** These departments generate the most revenue. Prioritize inventory, promotions, and operational efficiency here.")


    # --- 1. Pareto Chart: Department Sales Contribution ---
    st.markdown("### 📊 Pareto Chart: Department Sales Contribution")

    # Group by department, sum sales
    dept_sales = (
        df_filtered.groupby('Dept_Name')['Weekly_Sales']
        .sum()
        .reset_index()
        .sort_values('Weekly_Sales', ascending=False)
    )

    # Calculate cumulative sum and cumulative percentage
    dept_sales['Cumulative_Sales'] = dept_sales['Weekly_Sales'].cumsum()
    total_sales = dept_sales['Weekly_Sales'].sum()
    dept_sales['Cumulative_Percent'] = 100 * dept_sales['Cumulative_Sales'] / total_sales

    # Plot
    fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])

    # Bar for sales by department
    fig_pareto.add_trace(
        go.Bar(
            x=dept_sales['Dept_Name'],
            y=dept_sales['Weekly_Sales'],
            name='Department Sales',
            marker_color='royalblue',
            text=[f"${v:,.0f}" for v in dept_sales['Weekly_Sales']],
            textposition='auto'
        ),
        secondary_y=False
    )

    # Line for cumulative %
    fig_pareto.add_trace(
        go.Scatter(
            x=dept_sales['Dept_Name'],
            y=dept_sales['Cumulative_Percent'],
            name='Cumulative Sales %',
            mode='lines+markers',
            line=dict(color='orange', width=3),
            marker=dict(size=7)
        ),
        secondary_y=True
    )

    fig_pareto.update_layout(
        title_text="Pareto Chart - Department Sales Contribution",
        xaxis_tickangle=-45,
        margin=dict(t=60, b=140),
        height=600,
        legend=dict(x=0.7, y=1.1),
        template="plotly_white"
    )

    fig_pareto.update_yaxes(title_text="Sales ($)", secondary_y=False)
    fig_pareto.update_yaxes(title_text="Cumulative Sales (%)", secondary_y=True, range=[0, 110])

    st.plotly_chart(fig_pareto, use_container_width=True)

    st.info("""
    🔍 **Business Insight:**  
    This Pareto chart shows the cumulative sales contribution by department.  
    Focus on the first few departments that generate the majority of revenue (typically ~20%) to prioritize resources and maximize ROI.
    """)


    st.markdown("---")

    # --- 2. Underperforming Departments ---
    st.markdown("### 📉 Underperforming Departments (Bottom 20%)")
    total_sales_by_dept = (
        df_filtered.groupby('Dept_Name')['Weekly_Sales']
        .sum()
        .reset_index()
    )
    threshold = total_sales_by_dept['Weekly_Sales'].quantile(0.20)
    underperforming = total_sales_by_dept[total_sales_by_dept['Weekly_Sales'] <= threshold]

    fig_underperf = px.bar(
        underperforming,
        x='Dept_Name',
        y='Weekly_Sales',
        title="Departments with Lowest Total Sales",
        labels={'Dept_Name': 'Department', 'Weekly_Sales': 'Total Sales'},
        color='Weekly_Sales',
        color_continuous_scale='OrRd'
    )
    st.plotly_chart(fig_underperf, use_container_width=True)
    st.info("🔍 **Insight:** These areas may need rethinking. Consider markdowns, bundling, or reducing shelf space to optimize performance.")

    st.markdown("---")

    # --- 3. Departments with High Sales Variability ---
    st.markdown("### 📊 High Variability Departments")
    dept_var = (
        df_filtered.groupby('Dept_Name')['Weekly_Sales']
        .agg(['mean', 'std'])
        .reset_index()
    )
    dept_var['cv'] = dept_var['std'] / dept_var['mean']
    top_var = dept_var.sort_values('cv', ascending=False).head(10)

    fig_var = px.bar(
        top_var,
        x='Dept_Name',
        y='cv',
        title="Top 10 Departments by Sales Volatility",
        labels={'Dept_Name': 'Department', 'cv': 'Sales Variability'},
        color='cv',
        color_continuous_scale='Plasma'
    )
    st.plotly_chart(fig_var, use_container_width=True)
    st.info("🔍 **Insight:** These departments are inconsistent. Consider deeper analysis: does seasonality, promotion, or stock issue explain it? Stability helps with supply chain and staffing.")

    st.markdown("---")

    # --- 4. Holiday vs Non-Holiday Sales Comparison ---
    st.markdown("### 🎯 Holiday vs Non-Holiday Sales")

    avg_holiday_sales = df_filtered[df_filtered['IsHoliday_x'] == True]['Weekly_Sales'].mean()
    avg_nonholiday_sales = df_filtered[df_filtered['IsHoliday_x'] == False]['Weekly_Sales'].mean()

    df_holiday_compare = pd.DataFrame({
        'Week Type': ['Holiday Weeks', 'Non-Holiday Weeks'],
        'Average Weekly Sales': [avg_holiday_sales, avg_nonholiday_sales]
    })

    fig_compare = px.bar(
        df_holiday_compare,
        x='Week Type',
        y='Average Weekly Sales',
        color='Average Weekly Sales',
        text='Average Weekly Sales',
        color_continuous_scale='Sunset'
    )
    fig_compare.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    st.plotly_chart(fig_compare, use_container_width=True)
    st.info("🔍 **Insight:** Use this to gauge if holiday-focused strategies are paying off. If holidays outperform, ramp up marketing and stock in those periods.")

    st.markdown("---")

    # --- 5. Sales by Specific Holidays ---
    st.markdown("### 📅 Sales by Specific Holidays")

    # Recreate Holiday_Type
    df_filtered['Holiday_Type'] = 'None'
    df_filtered.loc[df_filtered['IsSuperBowl'] == True, 'Holiday_Type'] = 'Super Bowl'
    df_filtered.loc[df_filtered['IsLaborDay'] == True, 'Holiday_Type'] = 'Labor Day'
    df_filtered.loc[df_filtered['IsThanksgiving'] == True, 'Holiday_Type'] = 'Thanksgiving'
    df_filtered.loc[df_filtered['IsChristmas'] == True, 'Holiday_Type'] = 'Christmas'

    holiday_totals = (
        df_filtered[df_filtered['Holiday_Type'] != 'None']
        .groupby('Holiday_Type')['Weekly_Sales']
        .sum()
        .reset_index()
        .rename(columns={'Weekly_Sales': 'Total Sales'})
    )

    fig_specific = px.bar(
        holiday_totals,
        x='Holiday_Type',
        y='Total Sales',
        title="📅 Total Sales by Holiday",
        color='Total Sales',
        color_continuous_scale='agsunset'
    )
    st.plotly_chart(fig_specific, use_container_width=True)
    st.info("🔍 **Insight:** Not all holidays perform equally. This helps you know which events deserve priority focus in stock planning and ad budgets.")

    st.markdown("---")

    # --- 6. Holiday Sales Lift vs Non-Holiday Weeks ---
    st.markdown("### 📈 Holiday Sales Lift (%)")

    base = df_filtered[df_filtered['Holiday_Type'] == 'None']['Weekly_Sales'].sum()
    holiday_totals['Sales_Lift_%'] = ((holiday_totals['Total Sales'] / base) - 1) * 100

    fig_lift = px.bar(
        holiday_totals,
        x='Holiday_Type',
        y='Sales_Lift_%',
        title="📈 Holiday Sales Uplift vs Normal Weeks",
        labels={'Sales_Lift_%': 'Sales Lift (%)'},
        color='Sales_Lift_%',
        color_continuous_scale='Teal'
    )
    st.plotly_chart(fig_lift, use_container_width=True)
    st.info("🔍 **Insight:** Sales lift tells you which holidays outperform normal weeks. Combine this with gross margin data to know where to push hardest.")

    st.markdown("---")

    # --- 7. Markdown Impact ---
    st.markdown("### 🏷️ Markdowns and Sales")

    markdown_cols = ['MarkDown1', 'MarkDown2', 'MarkDown3', 'MarkDown4', 'MarkDown5']
    markdown_avg = {
        col: df_filtered[df_filtered[col] > 0]['Weekly_Sales'].mean()
        for col in markdown_cols if col in df_filtered.columns
    }

    markdown_df = pd.DataFrame({
        'Markdown Type': list(markdown_avg.keys()),
        'Avg Weekly Sales (When Used)': list(markdown_avg.values())
    }).sort_values('Avg Weekly Sales (When Used)', ascending=False)

    fig_markdown = px.bar(
        markdown_df,
        x='Markdown Type',
        y='Avg Weekly Sales (When Used)',
        title="📉 Impact of Markdowns on Average Sales",
        color='Avg Weekly Sales (When Used)',
        color_continuous_scale='mint'
    )
    st.plotly_chart(fig_markdown, use_container_width=True)
    st.info("🔍 **Insight:** Markdowns work—but only some types truly drive volume. Avoid unnecessary discounts on ineffective markdowns.")


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