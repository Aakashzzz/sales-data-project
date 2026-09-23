"""
Streamlit Dashboard — Data Cleaning & Visualization Project
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")

st.set_page_config(page_title="Sales Data Dashboard", layout="wide")
st.title("📊 Sales Data — Cleaning & Visualization Dashboard")

# -----------------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------------
RAW_PATH = "outputs/raw_sales_data.csv"

@st.cache_data
def load_and_clean(path):
    df = pd.read_csv(path, parse_dates=["OrderDate"])
    raw_shape = df.shape
    raw_missing = df.isna().sum()
    dup_count = df.duplicated().sum()

    df = df.drop_duplicates()
    df["Category"] = df["Category"].str.strip().str.title()
    df["Region"] = df["Region"].fillna("Unknown")
    df["UnitPrice"] = df.groupby("Category")["UnitPrice"].transform(lambda x: x.fillna(x.median()))
    df.loc[(df["CustomerAge"] < 10) | (df["CustomerAge"] > 100), "CustomerAge"] = np.nan
    df["CustomerAge"] = df["CustomerAge"].fillna(df["CustomerAge"].median())
    df["Revenue"] = df["UnitsSold"] * df["UnitPrice"]

    Q1, Q3 = df["UnitsSold"].quantile(0.25), df["UnitsSold"].quantile(0.75)
    IQR = Q3 - Q1
    lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    outlier_count = ((df["UnitsSold"] < lower) | (df["UnitsSold"] > upper)).sum()
    df["UnitsSold"] = df["UnitsSold"].clip(lower=lower, upper=upper)
    df["Revenue"] = df["UnitsSold"] * df["UnitPrice"]

    return df, raw_shape, raw_missing, dup_count, outlier_count

df, raw_shape, raw_missing, dup_count, outlier_count = load_and_clean(RAW_PATH)

# -----------------------------------------------------------------
# SIDEBAR FILTERS
# -----------------------------------------------------------------
st.sidebar.header("🔍 Filters")
regions = st.sidebar.multiselect("Region", sorted(df["Region"].unique()), default=sorted(df["Region"].unique()))
categories = st.sidebar.multiselect("Category", sorted(df["Category"].unique()), default=sorted(df["Category"].unique()))

filtered = df[df["Region"].isin(regions) & df["Category"].isin(categories)]

# -----------------------------------------------------------------
# CLEANING SUMMARY
# -----------------------------------------------------------------
st.subheader("🧹 Cleaning Summary")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Raw Rows", raw_shape[0])
c2.metric("Duplicates Removed", int(dup_count))
c3.metric("Outliers Capped", int(outlier_count))
c4.metric("Final Rows", df.shape[0])

with st.expander("See missing values (before cleaning)"):
    st.write(raw_missing[raw_missing > 0])

st.divider()

# -----------------------------------------------------------------
# KPIs
# -----------------------------------------------------------------
st.subheader("📈 Key Metrics")
k1, k2, k3 = st.columns(3)
k1.metric("Total Revenue", f"${filtered['Revenue'].sum():,.0f}")
k2.metric("Avg Order Revenue", f"${filtered['Revenue'].mean():,.0f}")
k3.metric("Avg Customer Age", f"{filtered['CustomerAge'].mean():.1f} yrs")

st.divider()

# -----------------------------------------------------------------
# CHARTS
# -----------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Revenue by Category**")
    cat_rev = filtered.groupby("Category")["Revenue"].sum().sort_values(ascending=False)
    st.bar_chart(cat_rev)

with col2:
    st.markdown("**Revenue by Region**")
    reg_rev = filtered.groupby("Region")["Revenue"].sum().sort_values(ascending=False)
    st.bar_chart(reg_rev)

st.markdown("**Monthly Revenue Trend**")
monthly = filtered.set_index("OrderDate").resample("ME")["Revenue"].sum()
st.line_chart(monthly)

col3, col4 = st.columns(2)

with col3:
    st.markdown("**UnitsSold Distribution (Outliers Capped)**")
    fig, ax = plt.subplots()
    sns.boxplot(x=filtered["UnitsSold"], ax=ax, color="lightskyblue")
    st.pyplot(fig)

with col4:
    st.markdown("**Customer Age Distribution**")
    fig, ax = plt.subplots()
    sns.histplot(filtered["CustomerAge"], bins=20, kde=True, ax=ax, color="mediumseagreen")
    st.pyplot(fig)

st.markdown("**Correlation Heatmap**")
fig, ax = plt.subplots(figsize=(6, 4))
numeric_cols = ["UnitsSold", "UnitPrice", "CustomerAge", "Revenue"]
sns.heatmap(filtered[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax, fmt=".2f")
st.pyplot(fig)

st.divider()
st.subheader("🗂️ Cleaned Data Preview")
st.dataframe(filtered.head(50))

st.download_button(
    "Download Cleaned CSV",
    filtered.to_csv(index=False).encode("utf-8"),
    "cleaned_sales_data.csv",
    "text/csv",
)
