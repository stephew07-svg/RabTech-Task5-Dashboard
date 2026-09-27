import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="RabTech KPI Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("clean_dataset.csv")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    return df

df = load_data()

st.title("Interactive Business KPI Dashboard")
st.caption("RabTech Academy – Task 5 | Built with Streamlit + Plotly")

# Sidebar filters
st.sidebar.header("Filters")
segments = st.sidebar.multiselect("Customer Segment", sorted(df["customer_segment"].dropna().unique()), default=sorted(df["customer_segment"].dropna().unique()))
categories = st.sidebar.multiselect("Category", sorted(df["category"].dropna().unique()), default=sorted(df["category"].dropna().unique()))
statuses = st.sidebar.multiselect("Payment Status", sorted(df["payment_status"].dropna().unique()), default=sorted(df["payment_status"].dropna().unique()))

f = df[df["customer_segment"].isin(segments) & df["category"].isin(categories) & df["payment_status"].isin(statuses)].copy()

revenue = f["net_sales"].sum()
orders = f["order_id"].nunique()
aov = revenue / orders if orders else 0
failed = (f["payment_status"].eq("Failed")).sum()
churn_rate = failed / len(f) * 100 if len(f) else 0
# CAC cannot be calculated from the supplied retail-orders fields because acquisition spend is not present.
cac = None

c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", f"₹{revenue:,.2f}")
c2.metric("Customer Acquisition Cost", "N/A")
c3.metric("Churn / Failed Order Rate", f"{churn_rate:.1f}%")
c4.metric("Average Order Value", f"₹{aov:,.2f}")

st.divider()

left, right = st.columns(2)

with left:
    monthly = f.assign(month=f["order_date"].dt.to_period("M").astype(str)).groupby("month", as_index=False)["net_sales"].sum()
    fig = px.area(monthly, x="month", y="net_sales", title="Revenue Trend")
    fig.update_layout(xaxis_title="Month", yaxis_title="Net Sales")
    st.plotly_chart(fig, use_container_width=True)

with right:
    cat = f.groupby("category", as_index=False)["net_sales"].sum().sort_values("net_sales", ascending=False)
    fig2 = px.bar(cat, x="category", y="net_sales", title="Revenue by Category")
    fig2.update_layout(xaxis_title="Category", yaxis_title="Net Sales")
    st.plotly_chart(fig2, use_container_width=True)

left2, right2 = st.columns(2)

with left2:
    city = f.groupby("city", as_index=False)["net_sales"].sum().sort_values("net_sales", ascending=False)
    fig3 = px.bar(city, x="city", y="net_sales", title="Revenue by City")
    fig3.update_layout(xaxis_title="City", yaxis_title="Net Sales")
    st.plotly_chart(fig3, use_container_width=True)

with right2:
    seg = f.groupby("customer_segment", as_index=False)["net_sales"].sum().sort_values("net_sales", ascending=False)
    fig4 = px.bar(seg, x="customer_segment", y="net_sales", title="Revenue by Customer Segment")
    fig4.update_layout(xaxis_title="Customer Segment", yaxis_title="Net Sales")
    st.plotly_chart(fig4, use_container_width=True)

st.subheader("Dashboard Data")
st.dataframe(f, use_container_width=True)

st.info("Note: CAC and true customer churn require additional fields such as acquisition spend and customer-level retention history. The dashboard therefore labels CAC as N/A and uses failed-order rate as a clearly defined operational proxy rather than presenting it as true customer churn.")
