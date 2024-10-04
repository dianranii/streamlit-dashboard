import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime

final_orders_df = pd.read_excel("final_order_data.xlsx")  
review_product_df = pd.read_csv("review_product_data.xls")  

final_orders_df['order_purchase_timestamp'] = pd.to_datetime(final_orders_df['order_purchase_timestamp'])

max_date = final_orders_df['order_purchase_timestamp'].max()

# Last six months data
last_six_months = final_orders_df[
    final_orders_df['order_purchase_timestamp'] >= (max_date - pd.DateOffset(months=6))
]

monthly_orders_df = last_six_months.resample(rule='M', on='order_purchase_timestamp').agg(
    order_count=('order_id', 'nunique'),  # Count unique orders
    revenue=('price', 'sum')              # Calculate total revenue
).reset_index()

monthly_orders_df['order_purchase_timestamp'] = monthly_orders_df['order_purchase_timestamp'].dt.strftime('%B-%Y')

st.subheader("Total Penjualan per Bulan dalam 6 Bulan Terakhir")
plt.figure(figsize=(10, 6))
sns.lineplot(data=monthly_orders_df, x='order_purchase_timestamp', y='revenue', marker='o', color='royalblue')
plt.title('Total Pendapatan per Bulan', fontsize=16)
plt.xlabel('Bulan', fontsize=12)
plt.ylabel('Pendapatan', fontsize=12)
plt.xticks(rotation=45)
plt.grid(visible=True, linestyle='--', alpha=0.7)
st.pyplot(plt)

# RFM Analysis for Last Month
one_month_ago = final_orders_df['order_purchase_timestamp'].max() - pd.DateOffset(months=1)
last_month_orders = final_orders_df[final_orders_df['order_purchase_timestamp'] >= one_month_ago]

rfm_last_month_df = last_month_orders.groupby('customer_id').agg({
    'order_purchase_timestamp': lambda x: (last_month_orders['order_purchase_timestamp'].max() - x.max()).days,  # Recency
    'order_id': 'count',  # Frequency
    'price': 'sum'  # Monetary
}).reset_index()

rfm_last_month_df.columns = ['customer_id', 'recency', 'frequency', 'monetary']

# Visualize purchase patterns
st.subheader("Visualisasi Pola Pembelian")

# Recency Distribution
plt.figure(figsize=(12, 6))
plt.subplot(1, 3, 1)
sns.histplot(rfm_last_month_df['recency'], bins=30, kde=True, color='skyblue')
plt.title('Distribusi Recency', fontsize=14)
plt.xlabel('Hari Sejak Pembelian Terakhir', fontsize=10)
plt.ylabel('Jumlah Pelanggan', fontsize=10)

# Frequency Distribution
plt.subplot(1, 3, 2)
sns.histplot(rfm_last_month_df['frequency'], bins=30, kde=True, color='lightgreen')
plt.title('Distribusi Frequency', fontsize=14)
plt.xlabel('Jumlah Pembelian', fontsize=10)
plt.ylabel('Jumlah Pelanggan', fontsize=10)

# Monetary Distribution
plt.subplot(1, 3, 3)
sns.histplot(rfm_last_month_df['monetary'], bins=30, kde=True, color='salmon')
plt.title('Distribusi Monetary', fontsize=14)
plt.xlabel('Total Pengeluaran', fontsize=10)
plt.ylabel('Jumlah Pelanggan', fontsize=10)

plt.tight_layout()
st.pyplot(plt)

# Category Analysis
st.subheader("Analisis Kategori Produk")
category_analysis = review_product_df.groupby('product_category_name').agg(
    average_review_score=('review_score', 'mean'),
    total_reviews=('review_score', 'count')
).reset_index()

top_categories = category_analysis.sort_values(by='average_review_score', ascending=False).head(10)
category_analysis['is_top'] = category_analysis['product_category_name'].isin(top_categories['product_category_name'])

# Plot category analysis
plt.figure(figsize=(12, 15))
sns.barplot(
    x='average_review_score', 
    y='product_category_name', 
    data=category_analysis, 
    hue='is_top',  
    palette=['skyblue', 'navy'],  
    legend=False  
)

plt.xlabel('Rata-rata Skor Ulasan', fontsize=12)
plt.ylabel('Kategori Produk', fontsize=12)
plt.title('Rata-rata Skor Ulasan Berdasarkan Kategori Produk', fontsize=16)
plt.grid(axis='x', linestyle='--', alpha=0.7)

st.pyplot(plt)
