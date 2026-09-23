# sales-data-project
Data cleaning &amp; visualization project on sales data — handles missing values, outliers &amp; duplicates using Pandas, with dashboards in Matplotlib/Seaborn &amp; Streamlit.
# 📊 Data Cleaning & Visualization Project

A complete data preprocessing and visualization pipeline built on a synthetic e-commerce sales dataset. This project demonstrates how to clean messy, real-world-style data and turn it into meaningful visual insights.

## 🎯 Objective

Take a raw dataset with common data quality issues and transform it into a clean, analysis-ready dataset — then visualize key business insights through static charts and an interactive dashboard.

## 🧹 Key Features

- **Missing Value Handling** — imputed using category-wise medians and logical fallbacks
- **Outlier Detection & Treatment** — IQR method used to detect and cap extreme values in `UnitsSold`
- **Duplicate Removal** — identified and removed duplicate order records
- **Data Standardization** — fixed inconsistent categorical text (e.g., "electronics" → "Electronics")
- **Visualization** — revenue by category/region, monthly sales trend, outlier boxplots, age distribution, and a correlation heatmap
- **Interactive Dashboard** — built with Streamlit, includes filters, KPIs, and downloadable cleaned data

## 🛠️ Tech Stack

- **Python**
- **Pandas** — data cleaning & transformation
- **NumPy** — numerical operations
- **Matplotlib & Seaborn** — static visualizations
- **Streamlit** — interactive dashboard

## 📁 Project Structure

```
├── outputs/
│   ├── raw_sales_data.csv        # Original raw dataset (with issues)
│   ├── cleaned_sales_data.csv    # Cleaned dataset after preprocessing
│   ├── dashboard.png             # Static visual insights dashboard
│   └── cleaning_report.txt       # Log of cleaning steps & key insights
├── clean_and_visualize.py        # Script: cleans data & generates dashboard.png
├── streamlit_app.py              # Interactive Streamlit dashboard
└── README.md
```

## 🚀 How to Run

**1. Install dependencies**
```bash
pip install pandas numpy matplotlib seaborn streamlit
```

**2. Run the cleaning & visualization script**
```bash
python clean_and_visualize.py
```

**3. Launch the interactive dashboard**
```bash
streamlit run streamlit_app.py
```

## 📈 Key Insights

- Best-selling category by revenue: **Electronics**
- Top-performing region: **North**
- Strongest sales month: **December**
- Dataset cleaned from 515 raw rows (with 15 duplicates, ~5% missing values, and outliers) down to 500 reliable rows

## 📚 What I Learned

- Practical data preprocessing techniques (handling nulls, outliers, duplicates)
- Exploratory Data Analysis (EDA) and storytelling with data
- Building both static and interactive dashboards
- End-to-end data pipeline from raw CSV to business insights
