"""Dashboard Penjualan Coffee Shop (Streamlit).
Jalankan: streamlit run app.py
"""
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Dashboard Penjualan Coffee Shop", page_icon="☕", layout="wide")

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
rupiah = lambda x: f"Rp {x:,.0f}".replace(",", ".")


@st.cache_data
def load_data(path="data/coffee_shop_sales_raw.csv"):
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset="transaction_id").copy()      # hapus transaksi dobel
    df["payment_method"] = df["payment_method"].fillna("Unknown")  # isi metode bayar kosong
    df["date"] = pd.to_datetime(df["date"])
    df["hour"] = df["time"].str[:2].astype(int)
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["day_name"] = df["date"].dt.day_name()
    return df


df = load_data()

# ---------- Sidebar filter ----------
st.sidebar.header("Filter")
d_min, d_max = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input("Rentang tanggal", (d_min, d_max), min_value=d_min, max_value=d_max)
cats = st.sidebar.multiselect("Kategori", sorted(df["category"].unique()), default=sorted(df["category"].unique()))
orders = st.sidebar.multiselect("Tipe pesanan", sorted(df["order_type"].unique()), default=sorted(df["order_type"].unique()))

if len(date_range) != 2:
    st.info("Pilih tanggal awal dan akhir.")
    st.stop()

f = df[
    df["date"].between(pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]))
    & df["category"].isin(cats)
    & df["order_type"].isin(orders)
]
if f.empty:
    st.warning("Tidak ada data untuk filter ini.")
    st.stop()

# ---------- Header & KPI ----------
st.title("☕ Dashboard Penjualan Coffee Shop")
st.caption("Periode Jan–Jun 2026 · dibuat dengan Python, Pandas, Plotly & Streamlit")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Pendapatan", rupiah(f["total_amount"].sum()))
c2.metric("Jumlah Transaksi", f"{f['transaction_id'].nunique():,}".replace(",", "."))
c3.metric("Rata-rata per Transaksi", rupiah(f["total_amount"].mean()))
c4.metric("Total Diskon Diberikan", rupiah(f["discount_amount"].sum()))

st.divider()

# ---------- Tren ----------
left, right = st.columns(2)
with left:
    st.subheader("Tren Pendapatan Bulanan")
    m = f.groupby("month", as_index=False)["total_amount"].sum()
    fig = px.bar(m, x="month", y="total_amount", text_auto=".2s", labels={"month": "Bulan", "total_amount": "Pendapatan (Rp)"})
    st.plotly_chart(fig, width="stretch")
with right:
    st.subheader("Pendapatan Harian")
    d = f.groupby("date", as_index=False)["total_amount"].sum()
    d["7-hari rata-rata"] = d["total_amount"].rolling(7).mean()
    fig = px.line(d, x="date", y=["total_amount", "7-hari rata-rata"], labels={"value": "Rp", "date": "Tanggal", "variable": ""})
    st.plotly_chart(fig, width="stretch")

# ---------- Produk ----------
left, right = st.columns(2)
prod = f.groupby("product", as_index=False).agg(pendapatan=("total_amount", "sum"), terjual=("quantity", "sum"))
with left:
    st.subheader("Top 10 Produk berdasarkan Pendapatan")
    t = prod.nlargest(10, "pendapatan").sort_values("pendapatan")
    fig = px.bar(t, x="pendapatan", y="product", orientation="h", text_auto=".2s", labels={"product": "", "pendapatan": "Pendapatan (Rp)"})
    st.plotly_chart(fig, width="stretch")
with right:
    st.subheader("Kontribusi Kategori")
    cat = f.groupby("category", as_index=False)["total_amount"].sum()
    fig = px.pie(cat, names="category", values="total_amount", hole=0.45)
    st.plotly_chart(fig, width="stretch")

# ---------- Jam & hari ----------
left, right = st.columns(2)
with left:
    st.subheader("Jam Sibuk (jumlah transaksi per jam)")
    h = f.groupby("hour", as_index=False).size()
    fig = px.bar(h, x="hour", y="size", labels={"hour": "Jam", "size": "Transaksi"})
    st.plotly_chart(fig, width="stretch")
with right:
    st.subheader("Heatmap Hari × Jam")
    hm = f.pivot_table(index="day_name", columns="hour", values="transaction_id", aggfunc="count", fill_value=0).reindex(DAY_ORDER)
    fig = px.imshow(hm, aspect="auto", color_continuous_scale="YlOrBr", labels={"x": "Jam", "y": "", "color": "Transaksi"})
    st.plotly_chart(fig, width="stretch")

# ---------- Pembayaran & pesanan ----------
left, right = st.columns(2)
with left:
    st.subheader("Metode Pembayaran")
    p = f.groupby("payment_method", as_index=False).size()
    fig = px.pie(p, names="payment_method", values="size", hole=0.45)
    st.plotly_chart(fig, width="stretch")
with right:
    st.subheader("Tipe Pesanan")
    o = f.groupby("order_type", as_index=False)["total_amount"].sum()
    fig = px.bar(o, x="order_type", y="total_amount", text_auto=".2s", labels={"order_type": "", "total_amount": "Pendapatan (Rp)"})
    st.plotly_chart(fig, width="stretch")

with st.expander("Lihat data transaksi"):
    st.dataframe(f.drop(columns=["hour", "month", "day_name"]), width="stretch")
