import os
import psycopg2
from datetime import datetime

# Konfigurasi Koneksi Database
DB_CONFIG = {
    "dbname": "mangs_base_db",
    "user": "postgres",
    "password": "sql177508",
    "host": "localhost"
}

def bersihkan_layar():
    os.system('cls' if os.name == 'nt' else 'clear')

def dapatkan_koneksi():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"[ERROR] Gagal terhubung ke database: {e}")
        return None

def tampilkan_menu(cursor):
    print("\n==============================================")
    print("         DAFTAR MENU MIE AYAM SAFIRNA         ")
    print("==============================================")
    print(f"{'ID':<4} | {'Nama Menu':<22} | {'Harga':<10} | {'Stok':<5}")
    print("----------------------------------------------")
    
    cursor.execute("SELECT id, nama_menu, harga, stok FROM menu ORDER BY id ASC")
    for row in cursor.fetchall():
        status_stok = "HABIS" if row[3] <= 0 else row[3]
        print(f"{row[0]:<4} | {row[1]:<22} | Rp{row[2]:<8} | {status_stok:<5}")
    print("==============================================\n")

def cetak_invoice(cursor, id_pesanan):
    # 1. Ambil data nota utama
    cursor.execute("SELECT tanggal, total_bayar FROM pesanan WHERE id = %s", (id_pesanan,))
    pesanan = cursor.fetchone()
    
    # 2. Ambil detail item yang dibeli
    cursor.execute("""
        SELECT m.nama_menu, d.jumlah, d.harga_satuan
        FROM pesanan_detail d
        JOIN menu m ON m.id = d.id_menu
        WHERE d.id_pesanan = %s
    """, (id_pesanan,))
    items = cursor.fetchall()

    # 3. Cetak Struk Belanjaan dengan Rapi (Lebar 40 Karakter)
    print("\n" + "="*40)
    print(" MIE AYAM SAFIRNA ".center(40, '*'))
    print("Jl. Gerobak No. 99 Jakarta".center(40))
    print("="*40)
    print(f"No Nota : #{id_pesanan:<10}")
    print(f"Tanggal : {pesanan[0].strftime('%d/%m/%Y %H:%M:%S')}")
    print("-" * 40)
    print(f"{'Menu':<20} {'Qty':>4} {'Subtotal':>13}")
    print("-" * 40)

    for nama, jumlah, harga in items:
        subtotal = jumlah * harga
        print(f"{nama:<20} {jumlah:>3}x  Rp{subtotal:>10}")

    print("-" * 40)
    print(f"{'TOTAL BELANJA':<24} Rp{pesanan[1]:>12}")
    print("="*40)
    print("TERIMA KASIH ATAS KUNJUNGAN ANDA".center(40))
    print("="*40 + "\n")

def buat_pesanan(conn, cursor):
    keranjang = []
    
    while True:
        tampilkan_menu(cursor)
        id_menu = input("Pilih ID Menu [Ketik 0 jika Selesai/Bayar]: ").strip()
        
        if id_menu == '0':
            break
            
        if not id_menu.isdigit():
            print("[Peringatan] ID Menu harus berupa angka!")
            continue
            
        # Cek apakah item sudah ada di keranjang sebelumnya
        if any(item['id'] == int(id_menu) for item in keranjang):
            print("[Peringatan] Menu sudah ada di keranjang belanja. Selesaikan dulu atau ganti menu.")
            continue

        cursor.execute("SELECT nama_menu, harga, stok FROM menu WHERE id = %s", (id_menu,))
        menu = cursor.fetchone()

        if not menu:
            print("[Peringatan] ID Menu tidak ditemukan!")
            continue

        nama_menu, harga, stok_sekarang = menu
        
        if stok_sekarang <= 0:
            print(f"[Peringatan] Maaf, {nama_menu} sudah habis!")
            continue

        jumlah_input = input(f"Masukkan Jumlah Beli {nama_menu} (Stok tersisa {stok_sekarang}): ").strip()
        if not jumlah_input.isdigit() or int(jumlah_input) <= 0:
            print("[Peringatan] Jumlah beli harus berupa angka bulat lebih dari 0!")
            continue
            
        jumlah = int(jumlah_input)

        if jumlah > stok_sekarang:
            print(f"[Peringatan] Stok tidak mencukupi! Hanya tersisa {stok_sekarang}.")
            continue

        # Masukkan ke keranjang belanja sementara
        keranjang.append({
            'id': int(id_menu),
            'nama': nama_menu,
            'jumlah': jumlah,
            'harga': harga
        })
        print(f"-> Berhasil menambah {jumlah}x {nama_menu} ke keranjang.")

    if not keranjang:
        print("\n[Info] Transaksi dibatalkan karena tidak ada item yang dipilih.")
        return

    # PROSES SIMPAN TRANSAKSI KE POSTGRESQL
    try:
        # Pembuatan Nota Induk Baru (total_bayar default 0, nanti diisi otomatis oleh trigger)
        cursor.execute("INSERT INTO pesanan DEFAULT VALUES RETURNING id;")
        id_pesanan = cursor.fetchone()[0]

        # Memasukkan detail item belanjaan
        for item in keranjang:
            cursor.execute("""
                INSERT INTO pesanan_detail (id_pesanan, id_menu, jumlah, harga_satuan)
                VALUES (%s, %s, %s, %s)
            """, (id_pesanan, item['id'], item['jumlah'], item['harga']))

        # Commit semua operasi jika berhasil tanpa kendala
        conn.commit()
        bersihkan_layar()
        print("\n[SUKSES] Transaksi Berhasil Disimpan ke Sistem Database!")
        
        # Cetak Invoice Akhir
        cetak_invoice(cursor, id_pesanan)

    except Exception as error:
        conn.rollback()
        print(f"\n[GAGAL SEPENUHNYA] Terjadi kesalahan sistem: {error}")
        print("Seluruh transaksi dibatalkan demi keamanan integritas data.")

def main():
    conn = dapatkan_koneksi()
    if not conn:
        return
        
    cursor = conn.cursor()
    
    while True:
        bersihkan_layar()
        buat_pesanan(conn, cursor)
        
        opsi = input("Apakah ada transaksi baru lagi? (y/n): ").strip().lower()
        if opsi != 'y':
            print("\nTerima kasih! Menutup sistem kasir Mie Ayam Safirna...")
            break
            
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()