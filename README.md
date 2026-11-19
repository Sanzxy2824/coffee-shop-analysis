# ☕ Analisis & Dashboard Penjualan Coffee Shop

Project portofolio analisis data: membersihkan data transaksi coffee shop (UMKM), menganalisis pola penjualan, dan menyajikannya dalam dashboard interaktif.

🔗 **Dashboard:** https://coffee-shop-dashboard-c39.streamlit.app/

**Tools:** Python, Pandas, Matplotlib, Seaborn, Plotly, Streamlit, Google Colab

## Pertanyaan Bisnis
1. Bagaimana tren pendapatan bulanan?
2. Produk dan kategori apa yang paling berkontribusi?
3. Jam dan hari apa yang paling ramai?
4. Bagaimana pola pembayaran, tipe pesanan, dan efek diskon?

## Dataset
2.505 baris transaksi (Januari–Juni 2026): tanggal, jam, produk, kategori, harga, jumlah, diskon, total, metode pembayaran, dan tipe pesanan.

## Pembersihan Data
- 5 transaksi dobel dihapus (2.505 → 2.500 transaksi)
- 12 data `payment_method` kosong diisi `Unknown`
- Total transaksi divalidasi (harga × jumlah − diskon)
- Ditambah fitur: jam, bulan, dan nama hari

## Temuan Utama
- Total pendapatan Rp77,3 juta, rata-rata Rp30.931 per transaksi
- Es Kopi Susu produk terlaris (Rp10,1 juta), disusul Matcha Latte
- Kopi 43,7% pendapatan, Non-Coffee 28,4%, Food 27,3%
- Jam sibuk: 12.00–14.00 dan 17.00–19.00
- Lebih dari 70% pembayaran non-tunai (QRIS terbanyak)
- Diskon tidak terlihat menaikkan nilai belanja per transaksi

## Rekomendasi
Tambah staf di jam sibuk, buat promo di jam sepi (pagi/malam), jadikan Es Kopi Susu dan Matcha Latte menu andalan, dan evaluasi ulang strategi diskon.

## Isi Repository
- `app.py`: dashboard Streamlit
- `data/`: dataset
- Notebook analisis (cleaning, EDA, insight): file `.ipynb`

---
Dibuat oleh **Ihsan Amiruddin**. Terbuka untuk jasa analisis data dan dashboard untuk UMKM.
