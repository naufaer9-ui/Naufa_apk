import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Kasir Mie Ayam Safirna", layout="wide")

# DAFTAR MENU BARU LENGKAP
MENU = [
    {"id": 1, "nama": "Mie Ayam", "harga": 10000, "stok": 999, "kategori": "Makanan"},
    {"id": 2, "nama": "Mie Ayam Bakso", "harga": 13000, "stok": 999, "kategori": "Makanan"},
    {"id": 3, "nama": "Maklor", "harga": 1000, "stok": 999, "kategori": "Camilan"},
    {"id": 4, "nama": "Cimin", "harga": 1000, "stok": 999, "kategori": "Camilan"},
    {"id": 5, "nama": "Teh Manis Panas", "harga": 3000, "stok": 999, "kategori": "Minuman"},
    {"id": 6, "nama": "Teh Manis Dingin", "harga": 3000, "stok": 999, "kategori": "Minuman"},
    {"id": 7, "nama": "Teh Pahit", "harga": 2000, "stok": 999, "kategori": "Minuman"},
    {"id": 8, "nama": "Jeruk Panas", "harga": 4000, "stok": 999, "kategori": "Minuman"},
    {"id": 9, "nama": "Jeruk Dingin", "harga": 4000, "stok": 999, "kategori": "Minuman"},
]

if 'nota_ke' not in st.session_state:
    st.session_state.nota_ke = 20
if 'keranjang' not in st.session_state:
    st.session_state.keranjang = []

st.title("🍜 MIE AYAM SAFIRNA")
st.caption("Jl. Gerobak No. 99 Jakarta")
st.divider()

col1, col2 = st.columns([1.2, 0.8])

with col1:
    st.subheader("📋 Pilih Menu")
    
    # Bikin tab biar gak panjang ke bawah
    tab1, tab2, tab3 = st.tabs(["🍜 Makanan", "🍢 Camilan", "🥤 Minuman"])
    
    with tab1:
        for m in [x for x in MENU if x['kategori'] == "Makanan"]:
            st.write(f"**{m['id']}. {m['nama']}** | Rp{m['harga']:,}")
    with tab2:
        for m in [x for x in MENU if x['kategori'] == "Camilan"]:
            st.write(f"**{m['id']}. {m['nama']}** | Rp{m['harga']:,}")
    with tab3:
        for m in [x for x in MENU if x['kategori'] == "Minuman"]:
            st.write(f"**{m['id']}. {m['nama']}** | Rp{m['harga']:,}")

    st.divider()
    with st.form("form_pesanan"):
        id_menu = st.selectbox("Pilih ID Menu", options=[m['id'] for m in MENU], format_func=lambda x: f"{x}. {next(m['nama'] for m in MENU if m['id']==x)}")
        qty = st.number_input("Jumlah", min_value=1, value=1, step=1)
        catatan = st.text_area("📝 Catatan untuk Dapur", placeholder="Contoh: Tanpa daun bawang, Extra sambal, Es dikit")
        tambah = st.form_submit_button("➕ Tambah ke Keranjang", use_container_width=True)
        
        if tambah:
            menu_pilih = next(m for m in MENU if m['id'] == id_menu)
            st.session_state.keranjang.append({**menu_pilih, "qty": qty, "catatan": catatan})
            st.success(f"Ditambah: {qty}x {menu_pilih['nama']}")

with col2:
    st.subheader("🧾 Keranjang Belanja")
    if st.session_state.keranjang:
        total = 0
        for i, item in enumerate(st.session_state.keranjang):
            subtotal = item['qty'] * item['harga']
            total += subtotal
            st.write(f"**{i+1}. {item['nama']}**")
            st.write(f" {item['qty']}x | Rp{subtotal:,}")
            if item['catatan']:
                st.caption(f" _Note: {item['catatan']}_")
            st.divider()
        
        st.metric("TOTAL BELANJA", f"Rp {total:,}")

        if st.button("✅ Bayar & Cetak Nota", type="primary", use_container_width=True):
            st.session_state.nota_ke += 1
            nota = st.session_state.nota_ke - 1
            
            st.balloons()
            st.success("[SUKSES] Transaksi Berhasil!")
            st.code(f"""
{''.center(40, '*')}
{'MIE AYAM SAFIRNA'.center(40, '*')}
{'Jl. Gerobak No. 99 Jakarta'.center(40)}
{''.center(40, '*')}
No Nota : #{nota}
Tanggal : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
{''.center(40, '-')}
""", language="")
            for item in st.session_state.keranjang:
                st.write(f"{item['nama']:<20} {item['qty']:>3}x Rp{item['qty']*item['harga']:>10}")
                if item['catatan']:
                    st.write(f" > Note: {item['catatan']}") 
            st.code(f"{''.center(40, '-')}\n{'TOTAL BELANJA':<24} Rp{total:>12}\n{''.center(40, '=')}", language="")
            
            st.session_state.keranjang = []
            st.rerun()
    else:
        st.info("Keranjang masih kosong. Pilih menu di sebelah 👈")
