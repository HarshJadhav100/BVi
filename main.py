import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.metric_cards import style_metric_cards

# Page config
st.set_page_config(page_title="Analytics Dashboard", page_icon="📈", layout="wide")

# Tooltip
st.markdown(
    '<p style="color: gray; font-size: 12px;">Use filters below. Visuals reflect filtered data. Data table is hidden.</p>',
    unsafe_allow_html=True
)
# Upload file from UI
uploaded_file = st.file_uploader("Upload your file", type=["csv", "xlsx"])

@st.cache_data
def load_data(file, file_type):
    if file_type == "csv":
        return pd.read_csv(file)
    elif file_type == "xlsx":
        return pd.read_excel(file)

# Use uploaded file or fallback to default
if uploaded_file is not None:
    file_type = uploaded_file.name.split(".")[-1].lower()
    df = load_data(uploaded_file, file_type)
else:
    st.info("No file uploaded. Using default data.csv")
    df = pd.read_csv("data.csv")

# Convert date column
df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')

# # Load data
# @st.cache_data
# def load_data():
#     return pd.read_csv('data.csv')

# df = load_data()
# df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')

# Hidden filter section (table not shown)
filtered_df = dataframe_explorer(df, case=False)

# Stop if empty
if filtered_df.empty:
    st.warning("No data after filtering. Adjust filters.")
    st.stop()

# Business Metrics
st.subheader("Business Metrics", divider="rainbow")
col1, col2 = st.columns(2)

with col1:
    bar_chart = alt.Chart(pd.DataFrame({
        "Quantity": filtered_df["Quantity"],
        "Product": filtered_df["Product"]
    })).mark_bar().encode(
        x="sum(Quantity):Q",
        y=alt.Y("Product:N", sort="-x")
    )
    st.altair_chart(bar_chart, use_container_width=True)

with col2:
    m1, m2 = st.columns(2)
    m1.metric("Total Products", filtered_df["Product"].count())
    m2.metric("Total Price (USD)", f"{filtered_df['TotalPrice'].sum():,.0f}")
    
    m3, m4, m5 = st.columns(3)
    m3.metric("Max Price", f"{filtered_df['TotalPrice'].max():,.0f}")
    m4.metric("Min Price", f"{filtered_df['TotalPrice'].min():,.0f}")
    m5.metric("Price Range", f"{filtered_df['TotalPrice'].max() - filtered_df['TotalPrice'].min():,.0f}")

    style_metric_cards(border_left_color="#415a7d", border_color="#1f66bd")

# 🔘 Dot Plot
col3, col4 = st.columns(2)

with col3:
    st.subheader("Products vs. Total Price", divider="rainbow")
    st.altair_chart(alt.Chart(filtered_df).mark_circle().encode(
        x='Product',
        y='TotalPrice',
        color='Category'
    ).interactive(), use_container_width=True)

with col4:
    st.subheader("Monthly Unit Price", divider="rainbow")
    month_chart = alt.Chart(filtered_df).mark_bar().encode(
        x="month(OrderDate):O",
        y="sum(UnitPrice):Q",
        color="Product:N"
    )
    st.altair_chart(month_chart, use_container_width=True)

# Scatter & Histogram
col5, col6 = st.columns(2)

with col5:
    st.subheader("Scatter Plot", divider="rainbow")
    x_feat = st.selectbox('X-axis Feature', filtered_df.select_dtypes("object").columns, key="scatter_x")
    y_feat = st.selectbox('Y-axis Feature', filtered_df.select_dtypes("number").columns, key="scatter_y")
    scatter_fig = px.scatter(
        filtered_df, x=x_feat, y=y_feat, color='Product',
        title=f'{x_feat} vs {y_feat}', template="plotly_white"
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

with col6:
    st.subheader("Histogram", divider="rainbow")
    hist_feat = st.selectbox("Select Feature", filtered_df.select_dtypes("object").columns, key="hist_feature")
    hist_fig = px.histogram(filtered_df, x=hist_feat, nbins=20, template="plotly_white")
    st.plotly_chart(hist_fig, use_container_width=True)
