"""
Data Cleaning & Visualization Project
--------------------------------------
Dataset: Synthetic e-commerce sales data (raw_sales_data.csv)
Steps:
  1. Load & inspect raw data
  2. Handle missing values
  3. Handle outliers
  4. Remove duplicates
  5. Fix inconsistent categorical entries
  6. Visualize key insights (Matplotlib + Seaborn)
  7. Export cleaned dataset + summary report
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 110

RAW_PATH = "outputs/raw_sales_data.csv"
CLEAN_PATH = "outputs/cleaned_sales_data.csv"

# -----------------------------------------------------------------
# 1. LOAD & INSPECT
# -----------------------------------------------------------------
df = pd.read_csv(RAW_PATH, parse_dates=["OrderDate"])
report = []
report.append(f"Raw dataset shape: {df.shape}")
report.append(f"Missing values per column:\n{df.isna().sum().to_string()}")
report.append(f"Duplicate rows: {df.duplicated().sum()}")

# -----------------------------------------------------------------
# 2. REMOVE DUPLICATES
# -----------------------------------------------------------------
before = len(df)
df = df.drop_duplicates()
report.append(f"Removed {before - len(df)} duplicate rows -> {len(df)} rows remain")

# -----------------------------------------------------------------
# 3. FIX INCONSISTENT CATEGORICAL TEXT
# -----------------------------------------------------------------
df["Category"] = df["Category"].str.strip().str.title()

# -----------------------------------------------------------------
# 4. HANDLE MISSING VALUES
# -----------------------------------------------------------------
# Region: unknown category -> fill with 'Unknown'
df["Region"] = df["Region"].fillna("Unknown")

# UnitPrice: fill with median price of same Category
df["UnitPrice"] = df.groupby("Category")["UnitPrice"].transform(
    lambda x: x.fillna(x.median())
)

# CustomerAge: fill with overall median age (after outlier cleanup below,
# but first mark implausible ages as missing so they don't skew the median)
df.loc[(df["CustomerAge"] < 10) | (df["CustomerAge"] > 100), "CustomerAge"] = np.nan
df["CustomerAge"] = df["CustomerAge"].fillna(df["CustomerAge"].median())

# Recompute Revenue wherever it's missing (UnitsSold * UnitPrice)
df["Revenue"] = df["UnitsSold"] * df["UnitPrice"]

report.append(f"Missing values after cleaning:\n{df.isna().sum().to_string()}")

# -----------------------------------------------------------------
# 5. HANDLE OUTLIERS (IQR method on UnitsSold)
# -----------------------------------------------------------------
Q1 = df["UnitsSold"].quantile(0.25)
Q3 = df["UnitsSold"].quantile(0.75)
IQR = Q3 - Q1
lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR

outlier_count = ((df["UnitsSold"] < lower) | (df["UnitsSold"] > upper)).sum()
report.append(f"UnitsSold outliers detected via IQR (bounds {lower:.1f}-{upper:.1f}): {outlier_count}")

# Cap (winsorize) instead of dropping, to preserve row count
df["UnitsSold"] = df["UnitsSold"].clip(lower=lower, upper=upper)
df["Revenue"] = df["UnitsSold"] * df["UnitPrice"]  # recompute after capping

# -----------------------------------------------------------------
# 6. EXPORT CLEANED DATA
# -----------------------------------------------------------------
df.to_csv(CLEAN_PATH, index=False)
report.append(f"Cleaned dataset saved: {CLEAN_PATH} | Final shape: {df.shape}")

# -----------------------------------------------------------------
# 7. VISUALIZATIONS
# -----------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Sales Data — Key Insights Dashboard", fontsize=16, fontweight="bold")

# (a) Revenue by Category
cat_rev = df.groupby("Category")["Revenue"].sum().sort_values(ascending=False)
sns.barplot(x=cat_rev.values, y=cat_rev.index, ax=axes[0, 0], palette="viridis", hue=cat_rev.index, legend=False)
axes[0, 0].set_title("Total Revenue by Category")
axes[0, 0].set_xlabel("Revenue ($)")
axes[0, 0].set_ylabel("")

# (b) Revenue by Region
reg_rev = df.groupby("Region")["Revenue"].sum().sort_values(ascending=False)
sns.barplot(x=reg_rev.index, y=reg_rev.values, ax=axes[0, 1], palette="crest", hue=reg_rev.index, legend=False)
axes[0, 1].set_title("Total Revenue by Region")
axes[0, 1].set_ylabel("Revenue ($)")

# (c) Monthly Revenue Trend
monthly = df.set_index("OrderDate").resample("ME")["Revenue"].sum()
axes[0, 2].plot(monthly.index, monthly.values, marker="o", color="darkorange")
axes[0, 2].set_title("Monthly Revenue Trend")
axes[0, 2].tick_params(axis="x", rotation=45)
axes[0, 2].set_ylabel("Revenue ($)")

# (d) UnitsSold distribution (post-outlier handling)
sns.boxplot(x=df["UnitsSold"], ax=axes[1, 0], color="lightskyblue")
axes[1, 0].set_title("UnitsSold Distribution (Outliers Capped)")

# (e) Customer Age distribution
sns.histplot(df["CustomerAge"], bins=20, kde=True, ax=axes[1, 1], color="mediumseagreen")
axes[1, 1].set_title("Customer Age Distribution")

# (f) Correlation heatmap
numeric_cols = ["UnitsSold", "UnitPrice", "CustomerAge", "Revenue"]
corr = df[numeric_cols].corr()
sns.heatmap(corr, annot=True, cmap="coolwarm", ax=axes[1, 2], fmt=".2f")
axes[1, 2].set_title("Correlation Heatmap")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("outputs/dashboard.png", bbox_inches="tight")
plt.close()

# -----------------------------------------------------------------
# 8. SAVE TEXT SUMMARY REPORT
# -----------------------------------------------------------------
top_category = cat_rev.idxmax()
top_region = reg_rev.idxmax()
best_month = monthly.idxmax().strftime("%B %Y")

insights = f"""
KEY INSIGHTS
------------
- Best-selling category by revenue: {top_category} (${cat_rev.max():,.2f})
- Top-performing region: {top_region} (${reg_rev.max():,.2f})
- Strongest sales month: {best_month} (${monthly.max():,.2f})
- Average order revenue: ${df['Revenue'].mean():,.2f}
- Average customer age: {df['CustomerAge'].mean():.1f} years
"""

with open("outputs/cleaning_report.txt", "w") as f:
    f.write("DATA CLEANING LOG\n==================\n")
    f.write("\n\n".join(report))
    f.write("\n\n" + insights)

print("\n".join(report))
print(insights)
print("Dashboard saved to outputs/dashboard.png")
