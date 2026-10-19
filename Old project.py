import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

FILENAME = 'Buku perpus'

class Buku:
    """Mewakili data satu buku Pinbook."""

    def __init__(self, id_buku, judul, penulis, jumlah_stok, harga):
        self.id = id_buku
        self.judul = judul
        self.penulis = penulis
        self.jumlah_stok = jumlah_stok
        self.harga = harga

    def __str__(self):
        return f"[{self.id}] '{self.judul}' oleh {self.penulis} (Stok: {self.jumlah_stok}, Harga: Rp {self.harga:,})"

    def hitung_total_harga(self, jumlah_beli):
        return jumlah_beli * self.harga

    def to_dict(self):
        return {
            "id": self.id,
            "judul": self.judul,
            "penulis": self.penulis,
            "jumlah_stok": self.jumlah_stok,
            "harga": self.harga,
        }


class TokoBuku:
    """Mengelola koleksi buku dan operasi CRUD."""

    def __init__(self):
        self.daftar_buku = []
        self.last_id = 0
        self.muat_data()

    def _get_new_id(self):
        """Menghasilkan ID unik baru."""
        self.last_id += 1
        return self.last_id

    def simpan_data(self):
        data_to_save = {
            "last_id": self.last_id,
            "buku": [buku.to_dict() for buku in self.daftar_buku],
        }
        try:
            with open(FILENAME, 'w') as f:
                json.dump(data_to_save, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error Sistem", f"Gagal menyimpan data: {e}")

    def muat_data(self):
        if os.path.exists(FILENAME):
            try:
                with open(FILENAME, 'r') as f:
                    data = json.load(f)
                    self.last_id = data.get("last_id", 0)
                    self.daftar_buku = []
                    for item in data.get("buku", []):
                        harga_buku = item.get('harga', 0)
                        stok_buku = item.get('jumlah_stok', 0)
                        buku_obj = Buku(
                            id_buku=item['id'],
                            judul=item['judul'],
                            penulis=item['penulis'],
                            jumlah_stok=stok_buku,
                            harga=harga_buku,
                        )
                        self.daftar_buku.append(buku_obj)
            except json.JSONDecodeError:
                messagebox.showwarning(
                    "Sistem", f"File {FILENAME} rusak. Memulai data baru."
                )
            except Exception as e:
                messagebox.showwarning(
                    "Sistem", f"Terjadi kesalahan saat memuat data: {e}. Memulai data baru."
                )
        else:
            pass

    def tambah_buku(self, judul, penulis, jumlah_stok, harga):
        """CREATE: Menambahkan buku baru ke koleksi."""
        new_id = self._get_new_id()
        buku_baru = Buku(new_id, judul, penulis, jumlah_stok, harga)
        self.daftar_buku.append(buku_baru)
        self.simpan_data()
        return True, f"Buku '{judul}' (ID: {new_id}) berhasil ditambahkan."

    def cari_buku_by_id(self, id_buku):
        """Mencari buku berdasarkan ID."""
        try:
            id_buku = int(id_buku)
        except ValueError:
            return None
        return next((b for b in self.daftar_buku if b.id == id_buku), None)

    def cari_buku(self, keyword):
        """READ: Mencari buku berdasarkan Judul atau Penulis."""
        keyword_lower = keyword.lower()
        hasil = [
            b
            for b in self.daftar_buku
            if keyword_lower in b.judul.lower() or keyword_lower in b.penulis.lower()
        ]
        return hasil

    def edit_buku(self, id_ubah, judul_baru, penulis_baru, stok_baru, harga_baru):
        """UPDATE: Mengubah detail buku."""
        buku = self.cari_buku_by_id(id_ubah)
        if not buku:
            return False, f"Buku dengan ID {id_ubah} tidak ditemukan."
        if judul_baru:
            buku.judul = judul_baru
        if penulis_baru:
            buku.penulis = penulis_baru
        if stok_baru is not None:
            buku.jumlah_stok = stok_baru
        if harga_baru is not None:
            buku.harga = harga_baru
        self.simpan_data()
        return True, f"Buku ID {id_ubah} berhasil diperbarui."

    def hapus_buku(self, id_hapus):
        """DELETE: Menghapus buku dari koleksi."""
        try:
            id_hapus = int(id_hapus)
        except ValueError:
            return False, "ID harus berupa angka."
        initial_length = len(self.daftar_buku)
        self.daftar_buku = [b for b in self.daftar_buku if b.id != id_hapus]
        if len(self.daftar_buku) < initial_length:
            self.simpan_data()
            return True, f"Buku ID {id_hapus} berhasil dihapus."
        else:
            return False, f"Buku dengan ID {id_hapus} tidak ditemukan."


# Isi GUI Tkinter
class PinbookApp:

    def __init__(self, master):
        self.master = master
        master.title("📚 Aplikasi Manajemen Pinbook")
        master.geometry("700x500")

        self.toko_buku = TokoBuku()

        # data demo jika file tidak ada
        if not self.toko_buku.daftar_buku and not os.path.exists(FILENAME):
            self._inisialisasi_data_demo()

        self.current_user = None
        self.login_frame = tk.Frame(master)
        self.login_frame.pack(pady=20, padx=20)
        self._setup_login_screen()

    def _inisialisasi_data_demo(self):
        """Data buku awal"""
        demo_books = [
            ("The Great Gatsby", "F. Scott Fitzgerald", 5, 85000),
            ("1984: A Modern Classic", "George Orwell", 3, 90000),
            ("Laskar Pelangi: Edisi Khusus", "Andrea Hirata", 2, 75000),
            ("The Metamorphosis", "Franz Kafka", 3, 60000),
            ("The Wings", "Yi Sang", 6, 95000),
            ("Don Quixote", "Miguel De Cervantes", 2, 120000),
            ("The Stranger", "Albert Camus", 5, 80000),
            ("Hell Screen", "Ryūnosuke Akutagawa", 1, 70000),
            ("Wuthering Heights", "Emily Brontë", 4, 110000),
            ("Faust", "Johann Wolfgang V.G", 3, 150000),
            ("Moby-Dick or, The Whale", "Herman Melville", 2, 130000),
            ("Crime and Punishment", "Fyodor Dostoevsky", 4, 105000),
            ("The Odyssey", "Homer", 6, 115000),
            ("The Golden Bough", "James George Frazer", 4, 95000),
            ("Dream of the Red Chamber", "Cao Xueqin", 5, 100000),
            ("Demian / Siddhartha", "Hermann Hesse", 6, 88000),
            ("The Divine Comedy: I-P-P", "Dante Alighieri", 7, 140000),
        ]
        for judul, penulis, stok, harga in demo_books:
            new_id = self.toko_buku._get_new_id()
            buku_baru = Buku(new_id, judul, penulis, stok, harga)
            self.toko_buku.daftar_buku.append(buku_baru)

        self.toko_buku.simpan_data()
        messagebox.showinfo("Sistem", f"Data demo ({len(demo_books)} buku) berhasil dimuat.")

    # Setup Layar Login
    def _setup_login_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.master.title("📚 Aplikasi Manajemen Pinbook - Login")
        self.master.geometry("400x300")

        login_frame = tk.Frame(self.master)
        login_frame.pack(pady=40, padx=40)

        tk.Label(login_frame, text="SELAMAT DATANG DI PINBOOK", font=('Arial', 14, 'bold')).pack(pady=10)
        tk.Label(login_frame, text="Pilih Peran Anda:", font=('Arial', 10)).pack(pady=5)

        tk.Button(
            login_frame,
            text="🔑 Login sebagai Admin",
            command=lambda: self._handle_login('admin'),
            bg='lightblue',
        ).pack(fill='x', pady=5)
        tk.Button(
            login_frame,
            text="🛒 Masuk sebagai Pembeli",
            command=lambda: self._handle_login('pembeli'),
            bg='lightgreen',
        ).pack(fill='x', pady=5)
        tk.Button(
            login_frame,
            text="🚪 Keluar Aplikasi",
            command=self.master.quit,
            bg='salmon',
        ).pack(fill='x', pady=5)

    # Tkinter untuk login sebagai Admin
    def _handle_login(self, role):
        if role == 'admin':
            password = simpledialog.askstring("Login Admin", "Masukkan Password Admin:", show='*')
            if password == "123":
                self.current_user = 'admin'
                self._setup_admin_screen()
            elif password is not None:
                messagebox.showerror("Login Gagal", "Password salah.")
        elif role == 'pembeli':
            self.current_user = 'pembeli'
            self._setup_pembeli_screen()

    # Layar Admin (CRUD)
    def _setup_admin_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.master.title("📚 Halaman Admin - Manajemen Inventaris")
        self.master.geometry("700x500")

        admin_frame = tk.Frame(self.master)
        admin_frame.pack(fill='both', expand=True, padx=10, pady=10)

        tk.Label(
            admin_frame,
            text="MANAJEMEN INVENTARIS BUKU (ADMIN)",
            font=('Arial', 12, 'bold'),
        ).pack(pady=10)

        # Frame untuk tombol CRUD
        button_frame = tk.Frame(admin_frame)
        button_frame.pack(pady=5)

        tk.Button(
            button_frame,
            text="➕ Tambah Buku",
            command=self._open_add_book_dialog,
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            button_frame,
            text="🔄 Refresh/Lihat Semua",
            command=lambda: self._display_books(self.admin_display_frame, is_admin=True),
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            button_frame,
            text="✏️ Edit Buku",
            command=self._open_edit_book_dialog,
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            button_frame,
            text="🗑️ Hapus Buku",
            command=self._open_delete_book_dialog,
        ).pack(side=tk.LEFT, padx=5)

        # Area untuk menampilkan daftar buku
        self.admin_display_frame = tk.Frame(admin_frame)
        self.admin_display_frame.pack(fill='both', expand=True, pady=10)
        self._display_books(self.admin_display_frame, is_admin=True)

        tk.Button(
            admin_frame,
            text="🚪 Logout / Kembali",
            command=self._setup_login_screen,
            bg='lightcoral',
        ).pack(side=tk.BOTTOM, pady=10)

    def _open_add_book_dialog(self):
        AddBookDialog(
            self.master,
            self.toko_buku,
            self._display_books,
            self.admin_display_frame,
            is_admin=True,
        )

    def _open_edit_book_dialog(self):
        EditBookDialog(
            self.master,
            self.toko_buku,
            self._display_books,
            self.admin_display_frame,
        )

    def _open_delete_book_dialog(self):
        DeleteBookDialog(
            self.master,
            self.toko_buku,
            self._display_books,
            self.admin_display_frame,
        )

    # Layar Pembeli, cuman bisa (READ dan Beli)
    def _setup_pembeli_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.master.title("🛒 Halaman Pembeli - Katalog Buku")
        self.master.geometry("700x500")

        pembeli_frame = tk.Frame(self.master)
        pembeli_frame.pack(fill='both', expand=True, padx=10, pady=10)

        tk.Label(
            pembeli_frame,
            text="KATALOG BUKU PINBOOK (PEMBELI)",
            font=('Arial', 12, 'bold'),
        ).pack(pady=10)

        # Frame untuk tombol Pembeli
        button_frame = tk.Frame(pembeli_frame)
        button_frame.pack(pady=5)

        tk.Button(
            button_frame,
            text="🔄 Refresh Katalog",
            command=lambda: self._display_books(self.pembeli_display_frame, is_admin=False),
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            button_frame,
            text="🔍 Cari Buku",
            command=self._open_search_dialog,
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            button_frame,
            text="🛍️ Beli Buku",
            command=self._open_purchase_dialog,
        ).pack(side=tk.LEFT, padx=5)

        # Area untuk menampilkan daftar buku
        self.pembeli_display_frame = tk.Frame(pembeli_frame)
        self.pembeli_display_frame.pack(fill='both', expand=True, pady=10)
        self._display_books(self.pembeli_display_frame, is_admin=False)

        tk.Button(
            pembeli_frame,
            text="🚪 Logout / Kembali",
            command=self._setup_login_screen,
            bg='lightcoral',
        ).pack(side=tk.BOTTOM, pady=10)

    def _open_search_dialog(self):
        keyword = simpledialog.askstring("Cari Buku", "Masukkan Judul atau Penulis:")
        if keyword:
            hasil_cari = self.toko_buku.cari_buku(keyword)
            self._display_books(
                self.pembeli_display_frame,
                is_admin=False,
                data_tampil=hasil_cari,
                is_search=True,
            )

    def _open_purchase_dialog(self):
        PurchaseDialog(
            self.master,
            self.toko_buku,
            self._display_books,
            self.pembeli_display_frame,
        )

    # Fungsi Utama Menampilkan Buku (Digunakan Admin & Pembeli)
    def _display_books(
        self, parent_frame, is_admin=False, data_tampil=None, is_search=False
    ):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        if data_tampil is None:
            data_tampil = sorted(self.toko_buku.daftar_buku, key=lambda b: b.id)

        if not data_tampil:
            tk.Label(parent_frame, text="Tidak ada buku yang ditemukan.", fg='red').pack(pady=20)
            return

        columns = ("ID", "Judul Buku", "Penulis", "Stok", "Harga Satuan")
        self.tree = ttk.Treeview(parent_frame, columns=columns, show='headings')
        self.tree.pack(fill='both', expand=True)

        self.tree.heading("ID", text="ID", anchor=tk.W)
        self.tree.heading("Judul Buku", text="Judul Buku", anchor=tk.W)
        self.tree.heading("Penulis", text="Penulis", anchor=tk.W)
        self.tree.heading("Stok", text="Stok", anchor=tk.CENTER)
        self.tree.heading("Harga Satuan", text="Harga Satuan", anchor=tk.E)

        self.tree.column("ID", width=30, anchor=tk.W)
        self.tree.column("Judul Buku", width=180, anchor=tk.W)
        self.tree.column("Penulis", width=120, anchor=tk.W)
        self.tree.column("Stok", width=50, anchor=tk.CENTER)
        self.tree.column("Harga Satuan", width=120, anchor=tk.E)

        for b in data_tampil:
            harga_formatted = f"Rp {b.harga:,}"
            self.tree.insert(
                '',
                tk.END,
                values=(b.id, b.judul, b.penulis, b.jumlah_stok, harga_formatted),
            )

        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        if is_search:
            tk.Label(
                parent_frame,
                text=f"Ditemukan {len(data_tampil)} buku untuk pencarian.",
                fg='blue',
            ).pack(pady=5)
        elif is_admin:
            tk.Label(
                parent_frame,
                text=f"Total: {len(self.toko_buku.daftar_buku)} buku dalam inventaris.",
                fg='green',
            ).pack(pady=5)
        else:
            tk.Label(
                parent_frame,
                text=f"Katalog tersedia: {len(self.toko_buku.daftar_buku)} buku.",
                fg='green',
            ).pack(pady=5)


# Dialog Tambah Buku (Admin)
class AddBookDialog(simpledialog.Dialog):

    def __init__(self, parent, toko_buku, refresh_func, refresh_frame, is_admin):
        self.toko_buku = toko_buku
        self.refresh_func = refresh_func
        self.refresh_frame = refresh_frame
        self.is_admin = is_admin
        super().__init__(parent, "Tambah Buku Baru")

    def body(self, master):
        tk.Label(master, text="Judul:").grid(row=0, sticky="w", pady=5, padx=5)
        tk.Label(master, text="Penulis:").grid(row=1, sticky="w", pady=5, padx=5)
        tk.Label(master, text="Stok Awal:").grid(row=2, sticky="w", pady=5, padx=5)
        tk.Label(master, text="Harga (Rp):").grid(row=3, sticky="w", pady=5, padx=5)

        self.judul_entry = tk.Entry(master, width=40)
        self.penulis_entry = tk.Entry(master, width=40)
        self.stok_entry = tk.Entry(master, width=40)
        self.harga_entry = tk.Entry(master, width=40)

        self.judul_entry.grid(row=0, column=1, padx=5)
        self.penulis_entry.grid(row=1, column=1, padx=5)
        self.stok_entry.grid(row=2, column=1, padx=5)
        self.harga_entry.grid(row=3, column=1, padx=5)

        return self.judul_entry

    def apply(self):
        judul = self.judul_entry.get()
        penulis = self.penulis_entry.get()
        stok_str = self.stok_entry.get()
        harga_str = self.harga_entry.get()

        if not judul or not penulis or not stok_str or not harga_str:
            messagebox.showerror("Error Input", "Semua kolom harus diisi.")
            return

        try:
            stok = int(stok_str)
            harga = int(harga_str)
            if stok < 0 or harga <= 0:
                messagebox.showerror("Error Input", "Stok harus >= 0 dan Harga harus > 0.")
                return
        except ValueError:
            messagebox.showerror("Error Input", "Stok dan Harga harus berupa angka.")
            return

        sukses, pesan = self.toko_buku.tambah_buku(judul, penulis, stok, harga)
        if sukses:
            messagebox.showinfo("Sukses", pesan)
            self.refresh_func(self.refresh_frame, self.is_admin)
        else:
            messagebox.showerror("Gagal", pesan)


# Dialog Edit Buku (Admin)
class EditBookDialog(simpledialog.Dialog):

    def __init__(self, parent, toko_buku, refresh_func, refresh_frame):
        self.toko_buku = toko_buku
        self.refresh_func = refresh_func
        self.refresh_frame = refresh_frame
        self.buku_ditemukan = None
        super().__init__(parent, "Edit Detail Buku")

    def body(self, master):
        tk.Label(master, text="ID Buku yang akan diubah:").grid(row=0, sticky="w", pady=5, padx=5)
        self.id_entry = tk.Entry(master, width=15)
        self.id_entry.grid(row=0, column=1, padx=5, sticky='ew')
        tk.Button(master, text="Cari", command=self._cari_buku).grid(row=0, column=2, padx=5)

        self.detail_frame = tk.Frame(master)
        self.detail_frame.grid(row=1, column=0, columnspan=3, pady=10)

        tk.Label(self.detail_frame, text="Judul Baru:").grid(row=0, sticky="w", pady=5, padx=5)
        tk.Label(self.detail_frame, text="Penulis Baru:").grid(row=1, sticky="w", pady=5, padx=5)
        tk.Label(self.detail_frame, text="Stok Baru:").grid(row=2, sticky="w", pady=5, padx=5)
        tk.Label(self.detail_frame, text="Harga Baru (Rp):").grid(row=3, sticky="w", pady=5, padx=5)

        self.judul_entry = tk.Entry(self.detail_frame, width=40)
        self.penulis_entry = tk.Entry(self.detail_frame, width=40)
        self.stok_entry = tk.Entry(self.detail_frame, width=40)
        self.harga_entry = tk.Entry(self.detail_frame, width=40)

        self.judul_entry.grid(row=0, column=1, padx=5)
        self.penulis_entry.grid(row=1, column=1, padx=5)
        self.stok_entry.grid(row=2, column=1, padx=5)
        self.harga_entry.grid(row=3, column=1, padx=5)

        for child in self.detail_frame.winfo_children():
            if isinstance(child, tk.Entry):
                child.config(state='disabled')

        return self.id_entry

    def _cari_buku(self):
        id_ubah_str = self.id_entry.get()
        if not id_ubah_str:
            messagebox.showerror("Error", "Masukkan ID Buku.")
            return

        self.buku_ditemukan = self.toko_buku.cari_buku_by_id(id_ubah_str)
        if not self.buku_ditemukan:
            messagebox.showerror("Error", f"Buku dengan ID {id_ubah_str} tidak ditemukan.")
            for child in self.detail_frame.winfo_children():
                if isinstance(child, tk.Entry):
                    child.config(state='disabled')
            return

        self.judul_entry.config(state='normal')
        self.penulis_entry.config(state='normal')
        self.stok_entry.config(state='normal')
        self.harga_entry.config(state='normal')

        self.judul_entry.delete(0, tk.END)
        self.judul_entry.insert(0, self.buku_ditemukan.judul)
        self.penulis_entry.delete(0, tk.END)
        self.penulis_entry.insert(0, self.buku_ditemukan.penulis)
        self.stok_entry.delete(0, tk.END)
        self.stok_entry.insert(0, str(self.buku_ditemukan.jumlah_stok))
        self.harga_entry.delete(0, tk.END)
        self.harga_entry.insert(0, str(self.buku_ditemukan.harga))

        messagebox.showinfo(
            "Ditemukan", f"Buku '{self.buku_ditemukan.judul}' siap diubah. Isi kolom yang ingin diubah."
        )

    def apply(self):
        if not self.buku_ditemukan:
            messagebox.showerror("Error", "Anda harus mencari buku terlebih dahulu.")
            return

        judul_baru = self.judul_entry.get()
        penulis_baru = self.penulis_entry.get()
        stok_baru_str = self.stok_entry.get()
        harga_baru_str = self.harga_entry.get()

        judul_to_save = judul_baru if judul_baru != self.buku_ditemukan.judul else None
        penulis_to_save = penulis_baru if penulis_baru != self.buku_ditemukan.penulis else None
        stok_to_save = None
        harga_to_save = None

        try:
            stok_int = int(stok_baru_str)
            if stok_int < 0:
                messagebox.showerror("Error Input", "Stok harus non-negatif.")
                return
            if stok_int != self.buku_ditemukan.jumlah_stok:
                stok_to_save = stok_int
        except ValueError:
            messagebox.showerror("Error Input", "Stok harus berupa angka.")
            return

        try:
            harga_int = int(harga_baru_str)
            if harga_int <= 0:
                messagebox.showerror("Error Input", "Harga harus lebih dari 0.")
                return
            if harga_int != self.buku_ditemukan.harga:
                harga_to_save = harga_int
        except ValueError:
            messagebox.showerror("Error Input", "Harga harus berupa angka.")
            return

        sukses, pesan = self.toko_buku.edit_buku(
            self.buku_ditemukan.id, judul_to_save, penulis_to_save, stok_to_save, harga_to_save
        )
        if sukses:
            messagebox.showinfo("Sukses", pesan)
            self.refresh_func(self.refresh_frame, is_admin=True)
        else:
            messagebox.showerror("Gagal", pesan)


# Dialog Hapus Buku (Admin)
class DeleteBookDialog(simpledialog.Dialog):

    def __init__(self, parent, toko_buku, refresh_func, refresh_frame):
        self.toko_buku = toko_buku
        self.refresh_func = refresh_func
        self.refresh_frame = refresh_frame
        super().__init__(parent, "Hapus Buku")

    def body(self, master):
        tk.Label(master, text="ID Buku yang akan Dihapus:").grid(row=0, sticky="w", pady=10, padx=5)
        self.id_entry = tk.Entry(master, width=15)
        self.id_entry.grid(row=0, column=1, padx=5)
        return self.id_entry

    def apply(self):
        id_hapus_str = self.id_entry.get()
        if not id_hapus_str:
            messagebox.showerror("Error", "Masukkan ID Buku.")
            return
        try:
            id_hapus = int(id_hapus_str)
        except ValueError:
            messagebox.showerror("Error", "ID harus berupa angka.")
            return

        buku_ditemukan = self.toko_buku.cari_buku_by_id(id_hapus)
        if not buku_ditemukan:
            messagebox.showerror("Gagal", f"Buku dengan ID {id_hapus_str} tidak ditemukan.")
            return

        konfirmasi = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Anda yakin ingin menghapus buku '{buku_ditemukan.judul}' (ID: {id_hapus})?",
        )
        if konfirmasi:
            sukses, pesan = self.toko_buku.hapus_buku(id_hapus)
            if sukses:
                messagebox.showinfo("Sukses", pesan)
                self.refresh_func(self.refresh_frame, is_admin=True)
            else:
                messagebox.showerror("Gagal", pesan)


# Dialog Beli Buku (Pembeli)
class PurchaseDialog(simpledialog.Dialog):

    def __init__(self, parent, toko_buku, refresh_func, refresh_frame):
        self.toko_buku = toko_buku
        self.refresh_func = refresh_func
        self.refresh_frame = refresh_frame
        self.buku_ditemukan = None
        super().__init__(parent, "Beli Buku")

    def body(self, master):
        tk.Label(master, text="ID Buku yang akan Dibeli:").grid(row=0, sticky="w", pady=5, padx=5)
        self.id_entry = tk.Entry(master, width=15)
        self.id_entry.grid(row=0, column=1, padx=5, sticky='ew')
        tk.Button(master, text="Cari", command=self._cari_buku).grid(row=0, column=2, padx=5)

        self.info_label = tk.Label(master, text="Detail Buku: -", fg='blue')
        self.info_label.grid(row=1, column=0, columnspan=3, pady=5)

        tk.Label(master, text="Jumlah Beli:").grid(row=2, sticky="w", pady=5, padx=5)
        self.jumlah_entry = tk.Entry(master, width=15, state='disabled')
        self.jumlah_entry.grid(row=2, column=1, padx=5)

        self.total_label = tk.Label(
            master, text="Total Harga: Rp 0", font=('Arial', 10, 'bold'), fg='darkgreen'
        )
        self.total_label.grid(row=3, column=0, columnspan=3, pady=10)

        tk.Button(master, text="Hitung Total", command=self._hitung_total).grid(
            row=2, column=2, padx=5
        )

        return self.id_entry

    def _cari_buku(self):
        id_beli_str = self.id_entry.get()
        if not id_beli_str:
            messagebox.showerror("Error", "Masukkan ID Buku.")
            return

        self.buku_ditemukan = self.toko_buku.cari_buku_by_id(id_beli_str)
        if not self.buku_ditemukan:
            self.info_label.config(
                text=f"Detail Buku: ID {id_beli_str} tidak ditemukan.", fg='red'
            )
            self.jumlah_entry.config(state='disabled')
            self.total_label.config(text="Total Harga: Rp 0")
            return

        info = f"'{self.buku_ditemukan.judul}' | Stok: {self.buku_ditemukan.jumlah_stok} | Harga: Rp {self.buku_ditemukan.harga:,}"
        self.info_label.config(text=f"Detail Buku: {info}", fg='darkblue')
        self.jumlah_entry.config(state='normal')
        self.jumlah_entry.delete(0, tk.END)
        self.jumlah_entry.insert(0, '1')
        self._hitung_total()

    def _hitung_total(self):
        if not self.buku_ditemukan:
            self.total_label.config(text="Total Harga: Rp 0")
            return

        jumlah_str = self.jumlah_entry.get()
        if not jumlah_str:
            self.total_label.config(text="Total Harga: Rp 0")
            return

        try:
            jumlah_beli = int(jumlah_str)
            if jumlah_beli <= 0:
                self.total_label.config(text="Total Harga: Rp 0")
                return
            total_harga = self.buku_ditemukan.hitung_total_harga(jumlah_beli)
            self.total_label.config(text=f"Total Harga: Rp {total_harga:,}")
        except ValueError:
            self.total_label.config(text="Total Harga: Rp 0")
            messagebox.showerror("Error Input", "Jumlah beli harus berupa angka.")

    def apply(self):
        if not self.buku_ditemukan:
            messagebox.showerror("Error", "Cari buku yang akan dibeli terlebih dahulu.")
            return

        jumlah_str = self.jumlah_entry.get()
        if not jumlah_str:
            messagebox.showerror("Error", "Masukkan jumlah beli.")
            return

        try:
            jumlah_beli = int(jumlah_str)
            if jumlah_beli <= 0:
                messagebox.showerror("Error Input", "Jumlah beli harus lebih dari 0.")
                return
            if jumlah_beli > self.buku_ditemukan.jumlah_stok:
                messagebox.showerror(
                    "Stok Kurang",
                    f"Stok hanya {self.buku_ditemukan.jumlah_stok}. Jumlah beli terlalu banyak.",
                )
                return
        except ValueError:
            messagebox.showerror("Error Input", "Jumlah beli harus berupa angka.")
            return

        total_harga = self.buku_ditemukan.hitung_total_harga(jumlah_beli)
        konfirmasi = messagebox.askyesno(
            "Konfirmasi Pembelian",
            f"Beli {jumlah_beli}x '{self.buku_ditemukan.judul}' dengan total Rp {total_harga:,}? Lanjutkan?",
        )
        if konfirmasi:
            stok_baru = self.buku_ditemukan.jumlah_stok - jumlah_beli
            sukses, pesan = self.toko_buku.edit_buku(
                self.buku_ditemukan.id, None, None, stok_baru, None
            )
            if sukses:
                messagebox.showinfo(
                    "Pembelian Sukses",
                    f"Pembelian berhasil! Total: Rp {total_harga:,}. Stok '{self.buku_ditemukan.judul}' kini {stok_baru}.",
                )
                self.refresh_func(self.refresh_frame, is_admin=False)
            else:
                messagebox.showerror(
                    "Pembelian Gagal", "Terjadi kesalahan saat mengupdate inventaris."
                )


# Eksekusi Program Utama
if __name__ == "__main__":
    root = tk.Tk()
    app = PinbookApp(root)
    root.mainloop()

# password: 123
# ubah pw ke line 233
