import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Kasir Mie Ayam Safirna", layout="centered")

# Data Menu Dummy - gak pake DB dulu
MENU = [
    {"id": 1, "nama": "Mie Ayam Original", "harga": 10000, "stok": 99},
    {"id": 2, "nama": "Mie Ayam Baso", "harga": 15000, "stok": 50},
    {"id": 3, "nama": "Mie Ayam Ceker", "harga": 12000, "stok": 30},
]

# Init session state buat nyimpen nota
if 'nota_ke' not in st.session_state:
    st.session_state.nota_ke = 20
if 'keranjang' not in st.session_state:
    st.session_state.keranjang = []

st.title("🍜 MIE AYAM SAFIRNA")
st.caption("Jl. Gerobak No. 99 Jakarta")
st.divider()

# TAMPILIN MENU
st.subheader("📋 Daftar Menu")
for m in MENU:
    st.write(f"**{m['id']}. {m['nama']}** | Rp{m['harga']:,} | Stok: {m['stok']}")
st.divider()

# FORM INPUT
with st.form("form_pesanan"):
    id_menu = st.selectbox("Pilih Menu", options=[m['id'] for m in MENU], format_func=lambda x: f"{x}. {next(m['nama'] for m in MENU if m['id']==x)}")
    qty = st.number_input("Jumlah", min_value=1, value=1, step=1)
    tambah = st.form_submit_button("➕ Tambah ke Keranjang")
    
    if tambah:
        menu_pilih = next(m for m in MENU if m['id'] == id_menu)
        if qty > menu_pilih['stok']:
            st.error(f"Stok {menu_pilih['nama']} cuma {menu_pilih['stok']}")
        else:
            st.session_state.keranjang.append({**menu_pilih, "qty": qty})
            st.success(f"Ditambah: {qty}x {menu_pilih['nama']}")

# TAMPILIN KERANJANG & BAYAR
if st.session_state.keranjang:
    st.divider()
    st.subheader("🧾 Keranjang Belanja")
    total = 0
    for item in st.session_state.keranjang:
        subtotal = item['qty'] * item['harga']
        total += subtotal
        st.write(f"- {item['nama']} | {item['qty']}x | Rp{subtotal:,}")
    
    st.metric("TOTAL BELANJA", f"Rp {total:,}")

    if st.button("✅ Bayar & Cetak Nota"):
        st.session_state.nota_ke += 1
        nota = st.session_state.nota_ke - 1
        
        st.success("[SUKSES] Transaksi Berhasil Disimpan!")
        st.divider()
        st.markdown(f"""
        **{'*'*40}**
        **{'MIE AYAM SAFIRNA'.center(40, '*')}**
        Jl. Gerobak No. 99 Jakarta
        {'-'*40}
        No Nota : #{nota}
        Tanggal : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        {'-'*40}
        """)
        for item in st.session_state.keranjang:
            st.write(f"{item['nama']:<20} {item['qty']:>3}x  Rp{item['qty']*item['harga']:>10}")
        st.markdown(f"{'-'*40}\n**{'TOTAL BELANJA':<24} Rp{total:>12}**\n{'='*40}")
        
        st.session_state.keranjang = [] # Kosongin keranjang
        st.rerun()
