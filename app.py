"""Dashboard Penjualan Coffee Shop (Streamlit) - tampilan v2."""
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Coffee Shop Dashboard", page_icon="☕", layout="wide")

BROWN, CARAMEL, CREAM = "#6F4E37", "#C8A27A", "#FBF6F0"
PALETTE = ["#6F4E37", "#C8A27A", "#A47148", "#E3C9A8", "#8B5E3C", "#3B2A20"]
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
rupiah = lambda x: f"Rp {x:,.0f}".replace(",", ".")

st.markdown(f"""
<style>
.block-container {{padding-top: 1.5rem;}}
.hero {{background: linear-gradient(135deg, #3B2A20 0%, #6F4E37 100%); color: #FBF6F0;
        padding: 28px 32px; border-radius: 18px; margin-bottom: 18px;}}
.hero h1 {{color:#FBF6F0; margin:0; font-size: 2rem;}}
.hero p {{color:#E3C9A8; margin:6px 0 0 0;}}
.kpi {{background:#fff; border-radius:16px; padding:18px 20px; border-left:6px solid {CARAMEL};
       box-shadow:0 2px 10px rgba(59,42,32,.10);}}
.kpi .label {{font-size:.85rem; color:#8B5E3C; font-weight:600;}}
.kpi .value {{font-size:1.6rem; font-weight:800; color:#3B2A20; white-space:nowrap;}}
.insight {{background:#F1E4D3; border-radius:12px; padding:12px 16px; margin:8px 0 16px 0; color:#3B2A20;}}
h3 {{color:#6F4E37;}}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(path="data/coffee_shop_sales_raw.csv"):
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset="transaction_id").copy()
    df["payment_method"] = df["payment_method"].fillna("Unknown")
    df["date"] = pd.to_datetime(df["date"])
    df["hour"] = df["time"].str[:2].astype(int)
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["day_name"] = df["date"].dt.day_name()
    return df


def style(fig, h=360):
    fig.update_layout(height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#3B2A20"), margin=dict(l=10, r=10, t=10, b=10),
                      legend_title_text="")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#E8D9C5")
    return fig


def kpi(col, label, value):
    col.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div></div>',
                 unsafe_allow_html=True)


def insight(text):
    st.markdown(f'<div class="insight">💡 {text}</div>', unsafe_allow_html=True)


df = load_data()

# ---------- Sidebar ----------
st.sidebar.markdown("## ☕ Filter")
d_min, d_max = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input("Rentang tanggal", (d_min, d_max), min_value=d_min, max_value=d_max)
all_cats, all_orders = sorted(df["category"].unique()), sorted(df["order_type"].unique())
cats = st.sidebar.multiselect("Kategori", all_cats, default=all_cats)
orders = st.sidebar.multiselect("Tipe pesanan", all_orders, default=all_orders)
st.sidebar.caption("Dibuat oleh Ihsan Amiruddin")

if len(date_range) != 2:
    st.info("Pilih tanggal awal dan akhir.")
    st.stop()

f = df[df["date"].between(pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]))
       & df["category"].isin(cats) & df["order_type"].isin(orders)]
if f.empty:
    st.warning("Tidak ada data untuk filter ini.")
    st.stop()

# ---------- Header & KPI ----------
st.markdown("""<div class="hero"><h1>☕ Coffee Shop Sales Dashboard</h1>
<p>Analisis penjualan Januari–Juni 2026 · Python, Pandas, Plotly & Streamlit</p></div>""",
            unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
kpi(k1, "💰 Total Pendapatan", rupiah(f["total_amount"].sum()))
kpi(k2, "🧾 Jumlah Transaksi", f"{len(f):,}".replace(",", "."))
kpi(k3, "🛒 Rata-rata / Transaksi", rupiah(f["total_amount"].mean()))
kpi(k4, "🏷️ Total Diskon", rupiah(f["discount_amount"].sum()))
st.write("")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Tren", "🥐 Produk", "⏰ Waktu Ramai", "💳 Pembayaran & Pesanan"])

with tab1:
    a, b = st.columns(2)
    with a:
        st.subheader("Pendapatan Bulanan")
        m = f.groupby("month", as_index=False)["total_amount"].sum()
        fig = px.bar(m, x="month", y="total_amount", text_auto=".3s", color_discrete_sequence=[BROWN],
                     labels={"month": "", "total_amount": "Pendapatan (Rp)"})
        fig.update_traces(marker_cornerradius=8)
        st.plotly_chart(style(fig), width="stretch")
    with b:
        st.subheader("Pendapatan Harian")
        d = f.groupby("date", as_index=False)["total_amount"].sum()
        d["Rata-rata 7 hari"] = d["total_amount"].rolling(7).mean()
        d = d.rename(columns={"total_amount": "Harian"})
        fig = px.line(d, x="date", y=["Harian", "Rata-rata 7 hari"], color_discrete_sequence=[CARAMEL, BROWN],
                      labels={"value": "Rp", "date": ""})
        st.plotly_chart(style(fig), width="stretch")
    insight("Pendapatan stabil di kisaran Rp12–14 juta per bulan; April tertinggi.")

with tab2:
    prod = f.groupby("product", as_index=False).agg(pendapatan=("total_amount", "sum"), terjual=("quantity", "sum"))
    a, b = st.columns([3, 2])
    with a:
        st.subheader("Top 10 Produk (Pendapatan)")
        t = prod.nlargest(10, "pendapatan").sort_values("pendapatan")
        fig = px.bar(t, x="pendapatan", y="product", orientation="h", text_auto=".3s",
                     color="pendapatan", color_continuous_scale=["#E3C9A8", "#3B2A20"],
                     labels={"product": "", "pendapatan": "Pendapatan (Rp)"})
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style(fig, 420), width="stretch")
    with b:
        st.subheader("Kontribusi Kategori")
        cat = f.groupby("category", as_index=False)["total_amount"].sum()
        fig = px.pie(cat, names="category", values="total_amount", hole=0.5, color_discrete_sequence=PALETTE)
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(style(fig, 420), width="stretch")
    top = prod.nlargest(1, "pendapatan").iloc[0]
    insight(f"Produk dengan pendapatan tertinggi: <b>{top['product']}</b> ({rupiah(top['pendapatan'])}).")

with tab3:
    a, b = st.columns(2)
    with a:
        st.subheader("Transaksi per Jam")
        h = f.groupby("hour", as_index=False).size()
        fig = px.bar(h, x="hour", y="size", color_discrete_sequence=[BROWN], labels={"hour": "Jam", "size": "Transaksi"})
        fig.update_traces(marker_cornerradius=6)
        st.plotly_chart(style(fig), width="stretch")
    with b:
        st.subheader("Heatmap Hari × Jam")
        hm = f.pivot_table(index="day_name", columns="hour", values="transaction_id",
                           aggfunc="count", fill_value=0).reindex(DAY_ORDER)
        fig = px.imshow(hm, aspect="auto", color_continuous_scale=["#FBF6F0", "#C8A27A", "#3B2A20"],
                        labels={"x": "Jam", "y": "", "color": "Transaksi"})
        st.plotly_chart(style(fig), width="stretch")
    peak = f.groupby("hour").size().idxmax()
    insight(f"Jam tersibuk: <b>{peak}.00</b>. Siapkan staf dan stok lebih awal di jam-jam puncak.")

with tab4:
    a, b = st.columns(2)
    with a:
        st.subheader("Metode Pembayaran")
        p = f.groupby("payment_method", as_index=False).size()
        fig = px.pie(p, names="payment_method", values="size", hole=0.5, color_discrete_sequence=PALETTE)
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(style(fig), width="stretch")
    with b:
        st.subheader("Pendapatan per Tipe Pesanan")
        o = f.groupby("order_type", as_index=False)["total_amount"].sum()
        fig = px.bar(o, x="order_type", y="total_amount", text_auto=".3s", color_discrete_sequence=[CARAMEL],
                     labels={"order_type": "", "total_amount": "Pendapatan (Rp)"})
        fig.update_traces(marker_cornerradius=8)
        st.plotly_chart(style(fig), width="stretch")

with st.expander("📋 Lihat data transaksi"):
    st.dataframe(f.drop(columns=["hour", "month", "day_name"]), width="stretch")
