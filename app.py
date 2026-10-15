import csv
import os
import random
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from models import Menu

# ================================================================ KONFIGURASI
FILE_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "menu.csv")
HEADER_CSV = ["Nama Menu", "Harga", "Kategori", "Status", "Favorit"]
KATEGORI = ["Makanan", "Minuman", "Snack"]
STATUS = ["Tersedia", "Habis"]
URUTAN = ["Nama A-Z", "Termurah", "Termahal", "Favorit dulu"]

PAKAI_EMOJI = True  # ganti False jika emoji tampil kotak-kotak atau program error

FONT = "Segoe UI"
FONT_EMOJI = "Segoe UI Emoji"

PUTIH = "#FFFFFF"
HIJAU = "#1F6B49"
HIJAU_NAV = "#3A8A63"
KREM = "#FFF6E5"
ORANYE = "#F4733B"
MERAH = "#E8473B"
UNGU = "#8E5BD1"
ABU = "#7A6F63"
TEKS = "#3A2E25"
GARIS = "#EBDDC4"
ABU_HABIS = "#B9B2A5"

WARNA_KAT = {"Makanan": "#F4733B", "Minuman": "#1FA8B8", "Snack": "#8E5BD1"}
IKON_KAT = {"Makanan": "🍛", "Minuman": "🥤", "Snack": "🍿"}

# Kata kunci nama menu -> emoji (yang pertama cocok dipakai)
KATA_EMOJI = [
    ("nasi", "🍛"), ("mie", "🍜"), ("soto", "🍲"), ("bakso", "🥣"), ("geprek", "🍗"),
    ("ayam", "🍗"), ("sate", "🍢"), ("telur", "🍳"), ("gado", "🥗"), ("burger", "🍔"),
    ("pizza", "🍕"), ("roti", "🍞"), ("teh", "🧋"), ("kopi", "☕"), ("jeruk", "🍊"),
    ("jus", "🍹"), ("susu", "🥛"), ("air", "💧"), ("es ", "🧊"), ("keripik", "🍟"),
    ("pisang", "🍌"), ("donat", "🍩"), ("kue", "🍰"), ("coklat", "🍫"),
]

CARD_W, CARD_H = 210, 255


def contoh_data():
    return [
        Menu("Nasi Goreng", 12000, "Makanan", "Tersedia", True),
        Menu("Mie Ayam", 10000, "Makanan", "Tersedia", False),
        Menu("Soto Ayam", 13000, "Makanan", "Tersedia", True),
        Menu("Bakso Urat", 12000, "Makanan", "Tersedia", False),
        Menu("Ayam Geprek", 14000, "Makanan", "Habis", False),
        Menu("Gado-gado", 11000, "Makanan", "Tersedia", False),
        Menu("Es Teh Manis", 4000, "Minuman", "Tersedia", True),
        Menu("Jus Jeruk", 7000, "Minuman", "Tersedia", False),
        Menu("Kopi Susu", 8000, "Minuman", "Tersedia", True),
        Menu("Air Mineral", 3000, "Minuman", "Tersedia", False),
        Menu("Keripik Singkong", 5000, "Snack", "Habis", False),
        Menu("Pisang Goreng", 5000, "Snack", "Tersedia", False),
        Menu("Donat", 4000, "Snack", "Tersedia", False),
    ]


# ================================================================ UTIL
def em(simbol):
    return simbol if PAKAI_EMOJI else ""


def teks_em(simbol, teks):
    return f"{simbol} {teks}" if PAKAI_EMOJI else teks


def emoji_dari(m):
    if not PAKAI_EMOJI:
        return ""
    nama = str(m.nama_menu).lower()
    for kata, emoji in KATA_EMOJI:
        if kata in nama:
            return emoji
    return IKON_KAT.get(m.kategori, "🍽️")


def gelap(hex_warna, faktor=0.85):
    r, g, b = (int(hex_warna[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(r * faktor), int(g * faktor), int(b * faktor))


def bersihkan(wadah):
    for w in wadah.winfo_children():
        w.destroy()


# ================================================================ DATA (CSV)
def simpan_data(daftar_menu):
    with open(FILE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER_CSV)
        for m in daftar_menu:
            writer.writerow(m.to_list())


def muat_data():
    if not os.path.exists(FILE_CSV) or os.path.getsize(FILE_CSV) == 0:
        simpan_data(contoh_data())  # buat file contoh pertama kali

    daftar = []
    with open(FILE_CSV, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)  # lewati header
        for row in reader:
            if len(row) < 3:
                continue
            status = row[3] if len(row) > 3 and row[3] else "Tersedia"
            favorit = len(row) > 4 and row[4].strip().lower() in ("ya", "1", "true")
            daftar.append(Menu(row[0], row[1], row[2], status, favorit))
    return daftar


# ================================================================ FRAME YANG BISA DI-SCROLL
class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg=KREM):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.sb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.sb.set)
        self.sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.isi = tk.Frame(self.canvas, bg=bg)
        self._jendela = self.canvas.create_window((0, 0), window=self.isi, anchor="nw")
        self.isi.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(
            self._jendela, width=e.width))


# ================================================================ APLIKASI
class KantinApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kantin Ceria")
        self.geometry("1180x760")
        self.minsize(960, 640)
        self.configure(bg=KREM)

        self.data = muat_data()
        self.filter_kat = "Semua"
        self.kolom = 4
        self.sf_aktif = None
        self._job = None

        self.var_nama = tk.StringVar()
        self.var_harga = tk.StringVar()
        self.var_kat = tk.StringVar(value=KATEGORI[0])
        self.var_status = tk.StringVar(value=STATUS[0])
        self.var_fav = tk.BooleanVar(value=False)

        self._gaya()
        self._buat_header()
        self._buat_statusbar()
        self._buat_area()

        for v in (self.var_nama, self.var_harga, self.var_kat, self.var_status, self.var_fav):
            v.trace_add("write", lambda *a: self.render_preview())

        self.pindah("beranda")
        self.render_semua()
        self.render_preview()

        self.bind("<Configure>", self._saat_resize)
        self.bind_all("<MouseWheel>", self._roda)
        self.bind_all("<Button-4>", self._roda)
        self.bind_all("<Button-5>", self._roda)

    # ------------------------------------------------------------ Gaya & helper widget
    def _gaya(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Treeview", background=PUTIH, fieldbackground=PUTIH, foreground=TEKS,
                    rowheight=34, font=(FONT, 11), borderwidth=0)
        s.configure("Treeview.Heading", background=HIJAU, foreground=PUTIH,
                    font=(FONT, 11, "bold"), relief="flat", padding=8)
        s.map("Treeview.Heading", background=[("active", gelap(HIJAU))])
        s.map("Treeview", background=[("selected", ORANYE)],
              foreground=[("selected", PUTIH)])
        s.configure("TCombobox", padding=6)

    def _tombol(self, parent, teks, warna, perintah, fg=PUTIH):
        b = tk.Button(parent, text=teks, command=perintah, bg=warna, fg=fg,
                      activebackground=gelap(warna), activeforeground=fg,
                      font=(FONT, 10, "bold"), relief="flat", bd=0,
                      padx=16, pady=9, cursor="hand2")
        b.bind("<Enter>", lambda e: b.config(bg=gelap(warna)))
        b.bind("<Leave>", lambda e: b.config(bg=warna))
        return b

    def _judul(self, parent, teks, tombol_teks=None, perintah=None):
        f = tk.Frame(parent, bg=KREM)
        f.pack(fill="x", pady=(8, 10))
        kiri = tk.Frame(f, bg=KREM)
        kiri.pack(side="left")
        tk.Label(kiri, text=teks, font=(FONT, 17, "bold"), bg=KREM, fg=TEKS).pack(anchor="w")
        tk.Frame(kiri, bg=ORANYE, height=4, width=54).pack(anchor="w", pady=(4, 0))
        if tombol_teks:
            self._tombol(f, tombol_teks, "#E6DCCB", perintah, fg=TEKS).pack(side="right")

    def _kosong(self, parent, ikon, judul, teks):
        f = tk.Frame(parent, bg=PUTIH, padx=30, pady=26)
        f.pack(fill="x", padx=8, pady=8)
        tk.Label(f, text=ikon, font=(FONT_EMOJI, 34), bg=PUTIH, fg=ABU).pack()
        tk.Label(f, text=judul, font=(FONT, 13, "bold"), bg=PUTIH, fg=TEKS).pack()
        tk.Label(f, text=teks, font=(FONT, 10), bg=PUTIH, fg=ABU).pack()

    # ------------------------------------------------------------ Header + navigasi
    def _buat_header(self):
        header = tk.Frame(self, bg=HIJAU)
        header.pack(fill="x")

        kiri = tk.Frame(header, bg=HIJAU)
        kiri.pack(side="left", padx=24, pady=12)
        tk.Label(kiri, text=em("🍽️") or "K", font=(FONT_EMOJI, 22), bg=PUTIH, fg=TEKS,
                 width=3).pack(side="left", padx=(0, 12))
        teks = tk.Frame(kiri, bg=HIJAU)
        teks.pack(side="left")
        tk.Label(teks, text="KANTIN CERIA", font=(FONT, 20, "bold"),
                 bg=HIJAU, fg=PUTIH).pack(anchor="w")
        tk.Label(teks, text="Enak, murah, bikin ceria!", font=(FONT, 10),
                 bg=HIJAU, fg="#D6F2E3").pack(anchor="w")

        kanan = tk.Frame(header, bg=HIJAU)
        kanan.pack(side="right", padx=20)
        self.nav = {}
        for nama, teks_tombol in [
            ("beranda", teks_em("🏠", "Beranda")),
            ("menu", teks_em("🍜", "Menu")),
            ("favorit", teks_em("❤️", "Favorit (0)")),
            ("tambah", teks_em("➕", "Tambah")),
            ("kelola", teks_em("🧾", "Kelola")),
        ]:
            b = tk.Button(kanan, text=teks_tombol, font=(FONT, 10, "bold"), relief="flat",
                          bd=0, padx=14, pady=8, cursor="hand2",
                          command=lambda n=nama: self.pindah(n))
            b.pack(side="left", padx=3)
            self.nav[nama] = b

        # Kanopi kantin (belang merah-putih)
        self.kanopi = tk.Canvas(self, height=18, bg=KREM, highlightthickness=0)
        self.kanopi.pack(fill="x")
        self.kanopi.bind("<Configure>", self._gambar_kanopi)

    def _gambar_kanopi(self, event=None):
        c = self.kanopi
        c.delete("all")
        lebar = c.winfo_width()
        x, i = 0, 0
        while x < lebar:
            warna = MERAH if i % 2 == 0 else PUTIH
            c.create_rectangle(x, 0, x + 36, 6, fill=warna, outline="")
            c.create_arc(x, -6, x + 36, 18, start=180, extent=180, fill=warna, outline="")
            x += 36
            i += 1

    def _buat_statusbar(self):
        self.status_bar = tk.Label(self, text="Siap.", anchor="w", bg="#E6E1D0", fg=ABU,
                                   font=(FONT, 9), padx=14, pady=4)
        self.status_bar.pack(fill="x", side="bottom")

    def status(self, teks):
        self.status_bar.config(text=teks)

    # ------------------------------------------------------------ Area halaman
    def _buat_area(self):
        self.area = tk.Frame(self, bg=KREM)
        self.area.pack(fill="both", expand=True)
        self.area.rowconfigure(0, weight=1)
        self.area.columnconfigure(0, weight=1)

        self.halaman = {}
        for nama, fungsi in [
            ("beranda", self._buat_beranda),
            ("menu", self._buat_menu),
            ("favorit", self._buat_favorit),
            ("tambah", self._buat_tambah),
            ("kelola", self._buat_kelola),
        ]:
            sf = ScrollFrame(self.area)
            sf.grid(row=0, column=0, sticky="nsew")
            fungsi(sf.isi)
            self.halaman[nama] = sf

    def pindah(self, nama):
        self.halaman[nama].tkraise()
        self.sf_aktif = self.halaman[nama]
        self.sf_aktif.canvas.yview_moveto(0)
        for n, b in self.nav.items():
            aktif = n == nama
            b.config(bg=PUTIH if aktif else HIJAU_NAV,
                     fg=ORANYE if aktif else PUTIH,
                     activebackground=PUTIH if aktif else HIJAU,
                     activeforeground=ORANYE if aktif else PUTIH)
        if nama == "tambah":
            self.ent_nama.focus_set()

    def _roda(self, e):
        if self.sf_aktif is None:
            return
        if getattr(e, "num", None) == 4:
            arah = -1
        elif getattr(e, "num", None) == 5:
            arah = 1
        else:
            arah = -1 if e.delta > 0 else 1
        self.sf_aktif.canvas.yview_scroll(arah * 2, "units")

    # ------------------------------------------------------------ Kolom kartu responsif
    def _hitung_kolom(self):
        lebar = max(self.winfo_width(), 600) - 110
        return max(1, lebar // (CARD_W + 16))

    def _saat_resize(self, e):
        if e.widget is not self:
            return
        if self._job:
            self.after_cancel(self._job)
        self._job = self.after(150, self._cek_kolom)

    def _cek_kolom(self):
        self._job = None
        k = self._hitung_kolom()
        if k != self.kolom:
            self.kolom = k
            self.render_beranda()
            self.render_menu()
            self.render_favorit()

    # ------------------------------------------------------------ Kartu menu
    def buat_kartu(self, parent, m, interaktif=True):
        warna = WARNA_KAT.get(m.kategori, ORANYE)
        habis = m.status == "Habis"
        warna_atas = ABU_HABIS if habis else warna

        kartu = tk.Frame(parent, bg=PUTIH, width=CARD_W, height=CARD_H,
                         highlightthickness=1, highlightbackground=GARIS)
        kartu.pack_propagate(False)

        # Bagian atas berwarna + emoji
        atas = tk.Frame(kartu, bg=warna_atas, height=112)
        atas.pack(fill="x")
        atas.pack_propagate(False)
        ikon = emoji_dari(m) or str(m.nama_menu)[:1].upper()
        tk.Label(atas, text=ikon, font=(FONT_EMOJI, 38), bg=warna_atas,
                 fg=PUTIH).place(relx=0.5, rely=0.55, anchor="center")
        tk.Label(atas, text=m.kategori.upper(), font=(FONT, 8, "bold"), bg=PUTIH,
                 fg=warna_atas, padx=8, pady=1).place(x=10, y=10)

        love = tk.Label(atas, text="♥" if m.favorit else "♡", font=(FONT, 15), bg=PUTIH,
                        fg=MERAH if m.favorit else ABU, width=2,
                        cursor="hand2" if interaktif else "")
        love.place(relx=1.0, x=-10, y=8, anchor="ne")
        if interaktif:
            love.bind("<Button-1>", lambda e, mm=m: self.toggle_fav(mm))

        if habis:
            tk.Label(atas, text="HABIS", font=(FONT, 14, "bold"), fg=MERAH, bg=PUTIH,
                     padx=10, pady=1, relief="solid", bd=2).place(
                relx=0.5, rely=0.55, anchor="center")

        # Bagian isi
        isi = tk.Frame(kartu, bg=PUTIH, padx=14, pady=10)
        isi.pack(fill="both", expand=True)

        baris = tk.Frame(isi, bg=PUTIH)
        baris.pack(fill="x", side="bottom")
        tk.Label(baris, text="Tersedia" if not habis else "Habis",
                 font=(FONT, 9, "bold"), bg="#DFF3E7" if not habis else "#FBE0DD",
                 fg=HIJAU if not habis else MERAH, padx=10, pady=2).pack(side="left")
        if interaktif:
            tk.Button(baris, text="Ubah", command=lambda mm=m: self.toggle_status(mm),
                      font=(FONT, 9, "bold"), bg="#F3EAD8", fg=TEKS, relief="flat", bd=0,
                      padx=10, pady=3, cursor="hand2",
                      activebackground="#E9DABF").pack(side="right")

        tk.Label(isi, text=m.nama_menu, font=(FONT, 12, "bold"), bg=PUTIH, fg=TEKS,
                 anchor="w", justify="left", wraplength=CARD_W - 30).pack(anchor="w")
        tk.Label(isi, text=m.harga_rupiah(), font=(FONT, 15, "bold"), bg=PUTIH,
                 fg=warna).pack(anchor="w", pady=(2, 0))
        return kartu

    def isi_grid(self, wadah, daftar, maks=None):
        bersihkan(wadah)
        k = self.kolom if maks is None else min(self.kolom, maks)
        for i, m in enumerate(daftar):
            kartu = self.buat_kartu(wadah, m)
            kartu.grid(row=i // k, column=i % k, padx=8, pady=8, sticky="n")

    # ------------------------------------------------------------ Halaman: Beranda
    def _buat_beranda(self, p):
        p.configure(padx=26, pady=16)

        hero = tk.Frame(p, bg=ORANYE, padx=30, pady=24)
        hero.pack(fill="x")
        kiri = tk.Frame(hero, bg=ORANYE)
        kiri.pack(side="left")
        tk.Label(kiri, text=f"Selamat Datang! {em('👋')}", font=(FONT, 26, "bold"),
                 bg=ORANYE, fg=PUTIH).pack(anchor="w")
        tk.Label(kiri, text="Lihat menu hari ini, simpan makanan dan minuman favoritmu,\n"
                            "lalu kelola stok kantin dengan mudah.",
                 font=(FONT, 11), bg=ORANYE, fg=PUTIH, justify="left").pack(anchor="w", pady=(6, 14))
        tombol = tk.Frame(kiri, bg=ORANYE)
        tombol.pack(anchor="w")
        self._tombol(tombol, teks_em("🍜", "Lihat Menu"), PUTIH,
                     lambda: self.pindah("menu"), fg=ORANYE).pack(side="left")
        self._tombol(tombol, teks_em("🎲", "Pilihkan untukku"), HIJAU,
                     self.pilihkan).pack(side="left", padx=8)
        self.lbl_rekom = tk.Label(kiri, text="", font=(FONT, 12, "bold"), bg=ORANYE, fg=PUTIH)
        self.lbl_rekom.pack(anchor="w", pady=(12, 0))
        tk.Label(hero, text=em("🍛🥤🍟") or "KANTIN", font=(FONT_EMOJI, 44),
                 bg=ORANYE, fg=PUTIH).pack(side="right", padx=10)
        tk.Frame(p, bg="#FFC24B", height=6).pack(fill="x")

        # Kartu statistik
        stat = tk.Frame(p, bg=KREM)
        stat.pack(fill="x", pady=16)
        for i in range(4):
            stat.columnconfigure(i, weight=1, uniform="s")
        self.lbl_stat = {}
        for i, (kunci, judul, warna, ikon) in enumerate([
            ("total", "TOTAL MENU", ORANYE, "📋"),
            ("ada", "TERSEDIA", HIJAU, "✅"),
            ("habis", "HABIS", MERAH, "⛔"),
            ("fav", "FAVORIT", UNGU, "❤️"),
        ]):
            k = tk.Frame(stat, bg=PUTIH, padx=16, pady=12)
            k.grid(row=0, column=i, sticky="ew", padx=6)
            tk.Frame(k, bg=warna, width=5).pack(side="left", fill="y", padx=(0, 12))
            d = tk.Frame(k, bg=PUTIH)
            d.pack(side="left")
            tk.Label(d, text=teks_em(ikon, judul), font=(FONT, 9, "bold"),
                     bg=PUTIH, fg=ABU).pack(anchor="w")
            lbl = tk.Label(d, text="0", font=(FONT, 24, "bold"), bg=PUTIH, fg=warna)
            lbl.pack(anchor="w")
            self.lbl_stat[kunci] = lbl

        self._judul(p, teks_em("⭐", "Favorit Kantin"), "Lihat semua",
                    lambda: self.pindah("favorit"))
        self.grid_beranda = tk.Frame(p, bg=KREM)
        self.grid_beranda.pack(fill="x")

    def render_beranda(self):
        favs = [m for m in self.data if m.favorit][:4]
        if favs:
            self.isi_grid(self.grid_beranda, favs, maks=4)
        else:
            bersihkan(self.grid_beranda)
            self._kosong(self.grid_beranda, em("🤍") or "♡", "Belum ada favorit",
                         "Tekan tombol ♥ pada kartu menu untuk menambahkannya.")

    def pilihkan(self):
        ada = [m for m in self.data if m.status == "Tersedia"]
        if not ada:
            self.lbl_rekom.config(text="Semua menu sedang habis :(")
            return
        m = random.choice(ada)
        self.lbl_rekom.config(
            text=f"{em('🎲')} Cobain hari ini: {emoji_dari(m)} {m.nama_menu} - {m.harga_rupiah()}")

    # ------------------------------------------------------------ Halaman: Menu
    def _buat_menu(self, p):
        p.configure(padx=26, pady=16)
        self._judul(p, teks_em("🍜", "Menu Kantin"))

        bar = tk.Frame(p, bg=KREM)
        bar.pack(fill="x", pady=(0, 8))
        self.var_cari = tk.StringVar()
        self.var_urut = tk.StringVar(value=URUTAN[0])

        tk.Label(bar, text=em("🔍") or "Cari:", font=(FONT, 12), bg=KREM,
                 fg=ABU).pack(side="left", padx=(0, 6))
        ent = tk.Entry(bar, textvariable=self.var_cari, font=(FONT, 11), relief="flat",
                       bg=PUTIH, fg=TEKS, highlightthickness=2,
                       highlightbackground=GARIS, highlightcolor=ORANYE)
        ent.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 10))
        cb = ttk.Combobox(bar, textvariable=self.var_urut, values=URUTAN,
                          state="readonly", width=16, font=(FONT, 10))
        cb.pack(side="right")
        cb.bind("<<ComboboxSelected>>", lambda e: self.render_menu())
        self.var_cari.trace_add("write", lambda *a: self.render_menu())

        chips = tk.Frame(p, bg=KREM)
        chips.pack(fill="x", pady=6)
        self.chip = {}
        for nama in ["Semua"] + KATEGORI:
            b = tk.Button(chips, text=teks_em(IKON_KAT.get(nama, "🍽️"), nama),
                          font=(FONT, 10, "bold"), relief="flat", bd=0, padx=16, pady=7,
                          cursor="hand2", highlightthickness=2, highlightbackground=GARIS,
                          command=lambda n=nama: self.set_filter(n))
            b.pack(side="left", padx=(0, 8))
            self.chip[nama] = b
        self._gaya_chip()

        self.lbl_info = tk.Label(p, text="", bg=KREM, fg=ABU, font=(FONT, 9))
        self.lbl_info.pack(anchor="w", pady=(6, 4))
        self.grid_menu = tk.Frame(p, bg=KREM)
        self.grid_menu.pack(fill="x")

    def _gaya_chip(self):
        for nama, b in self.chip.items():
            aktif = nama == self.filter_kat
            b.config(bg=ORANYE if aktif else PUTIH, fg=PUTIH if aktif else ABU,
                     activebackground=gelap(ORANYE) if aktif else "#F3EAD8",
                     activeforeground=PUTIH if aktif else ABU)

    def set_filter(self, nama):
        self.filter_kat = nama
        self._gaya_chip()
        self.render_menu()

    def render_menu(self):
        kata = self.var_cari.get().strip().lower()
        daftar = [m for m in self.data
                  if (not kata or kata in m.nama_menu.lower())
                  and (self.filter_kat == "Semua" or m.kategori == self.filter_kat)]

        urut = self.var_urut.get()
        if urut == "Termurah":
            daftar.sort(key=lambda m: m.harga_angka())
        elif urut == "Termahal":
            daftar.sort(key=lambda m: m.harga_angka(), reverse=True)
        elif urut == "Favorit dulu":
            daftar.sort(key=lambda m: (not m.favorit, m.nama_menu.lower()))
        else:
            daftar.sort(key=lambda m: m.nama_menu.lower())

        if daftar:
            self.isi_grid(self.grid_menu, daftar)
        else:
            bersihkan(self.grid_menu)
            self._kosong(self.grid_menu, em("🔍") or "?", "Menu tidak ditemukan",
                         "Coba kata kunci atau kategori lain.")
        self.lbl_info.config(text=f"Menampilkan {len(daftar)} dari {len(self.data)} menu")

    # ------------------------------------------------------------ Halaman: Favorit
    def _buat_favorit(self, p):
        p.configure(padx=26, pady=16)
        self._judul(p, teks_em("❤️", "Makanan & Minuman Favorit"))
        self.wadah_fav = tk.Frame(p, bg=KREM)
        self.wadah_fav.pack(fill="x")

    def render_favorit(self):
        bersihkan(self.wadah_fav)
        favs = [m for m in self.data if m.favorit]
        if not favs:
            self._kosong(self.wadah_fav, em("🤍") or "♡", "Belum ada favorit",
                         "Buka halaman Menu lalu tekan ♥ pada menu yang kamu suka.")
            return
        for k in KATEGORI:
            daftar = [m for m in favs if m.kategori == k]
            if not daftar:
                continue
            tk.Label(self.wadah_fav, text=teks_em(IKON_KAT[k], f"{k} Favorit"),
                     font=(FONT, 12, "bold"), bg=WARNA_KAT[k], fg=PUTIH,
                     padx=16, pady=5).pack(anchor="w", pady=(14, 4))
            g = tk.Frame(self.wadah_fav, bg=KREM)
            g.pack(fill="x")
            self.isi_grid(g, daftar)

    # ------------------------------------------------------------ Halaman: Tambah
    def _segmen(self, parent, var, pilihan):
        f = tk.Frame(parent, bg=PUTIH)
        for nilai, teks in pilihan:
            tk.Radiobutton(f, text=teks, value=nilai, variable=var, indicatoron=False,
                           font=(FONT, 10, "bold"), bg="#F6EEDD", fg=TEKS,
                           selectcolor="#BFE3CF", activebackground="#EADFC8",
                           relief="flat", bd=0, padx=14, pady=8,
                           cursor="hand2").pack(side="left", padx=(0, 8))
        return f

    def _buat_tambah(self, p):
        p.configure(padx=26, pady=16)
        self._judul(p, teks_em("➕", "Tambah Menu Baru"))

        baris = tk.Frame(p, bg=KREM)
        baris.pack(fill="x", anchor="n")

        form = tk.Frame(baris, bg=PUTIH, padx=26, pady=22)
        form.pack(side="left", anchor="n")

        def label(teks):
            tk.Label(form, text=teks, font=(FONT, 9, "bold"), bg=PUTIH,
                     fg=ABU).pack(anchor="w", pady=(14, 4))

        def entri(var):
            e = tk.Entry(form, textvariable=var, font=(FONT, 12), relief="flat", width=34,
                         bg=PUTIH, fg=TEKS, highlightthickness=2,
                         highlightbackground=GARIS, highlightcolor=ORANYE)
            e.pack(anchor="w", ipady=7)
            return e

        label("NAMA MENU")
        self.ent_nama = entri(self.var_nama)
        label("HARGA (RP)")
        ent_harga = entri(self.var_harga)

        label("KATEGORI")
        self._segmen(form, self.var_kat, [
            ("Makanan", teks_em("🍛", "Makanan")),
            ("Minuman", teks_em("🥤", "Minuman")),
            ("Snack", teks_em("🍿", "Snack")),
        ]).pack(anchor="w")

        label("STATUS")
        self._segmen(form, self.var_status, [
            ("Tersedia", teks_em("✅", "Tersedia")),
            ("Habis", teks_em("⛔", "Habis")),
        ]).pack(anchor="w")

        tk.Checkbutton(form, text="Jadikan favorit ♥", variable=self.var_fav,
                       font=(FONT, 11, "bold"), bg=PUTIH, fg=TEKS, activebackground=PUTIH,
                       selectcolor=PUTIH, cursor="hand2").pack(anchor="w", pady=(18, 0))

        aksi = tk.Frame(form, bg=PUTIH)
        aksi.pack(anchor="w", pady=(22, 0))
        self._tombol(aksi, "Simpan Menu", HIJAU, self.tambah_menu).pack(side="left")
        self._tombol(aksi, "Bersihkan", "#8A8A8A", self.bersihkan_form).pack(side="left", padx=8)

        kanan = tk.Frame(baris, bg=KREM)
        kanan.pack(side="left", anchor="n", padx=30)
        tk.Label(kanan, text="PRATINJAU KARTU", font=(FONT, 9, "bold"), bg=KREM,
                 fg=ABU).pack(anchor="w", pady=(0, 8))
        self.wadah_preview = tk.Frame(kanan, bg=KREM)
        self.wadah_preview.pack()

        self.ent_nama.bind("<Return>", lambda e: self.tambah_menu())
        ent_harga.bind("<Return>", lambda e: self.tambah_menu())

    def render_preview(self):
        bersihkan(self.wadah_preview)
        try:
            harga = int(self.var_harga.get().replace(".", "").strip() or 0)
        except ValueError:
            harga = 0
        m = Menu(self.var_nama.get().strip() or "Nama Menu", harga, self.var_kat.get(),
                 self.var_status.get(), self.var_fav.get())
        self.buat_kartu(self.wadah_preview, m, interaktif=False).pack()

    def bersihkan_form(self):
        self.var_nama.set("")
        self.var_harga.set("")
        self.var_kat.set(KATEGORI[0])
        self.var_status.set(STATUS[0])
        self.var_fav.set(False)
        self.ent_nama.focus_set()

    def tambah_menu(self):
        nama = self.var_nama.get().strip()
        harga = self.var_harga.get().strip().replace(".", "")

        if not nama or not harga:
            messagebox.showwarning("Peringatan", "Nama menu dan harga harus diisi!")
            return
        if not harga.isdigit():
            messagebox.showwarning("Peringatan", "Harga harus berupa angka positif!")
            return

        self.data.append(Menu(nama, int(harga), self.var_kat.get(),
                              self.var_status.get(), self.var_fav.get()))
        self.simpan_dan_render(f"Menu '{nama}' berhasil ditambahkan.")
        self.bersihkan_form()
        self.pindah("menu")

    # ------------------------------------------------------------ Halaman: Kelola
    def _buat_kelola(self, p):
        p.configure(padx=26, pady=16)
        self._judul(p, teks_em("🧾", "Kelola Menu"))

        panel = tk.Frame(p, bg=PUTIH, padx=16, pady=16)
        panel.pack(fill="x")
        panel.columnconfigure(0, weight=1)

        kolom = ("nama", "harga", "kategori", "status", "fav")
        self.tree = ttk.Treeview(panel, columns=kolom, show="headings",
                                 selectmode="browse", height=11)
        for k, judul, lebar, anchor in [
            ("nama", "Nama Menu", 260, "w"),
            ("harga", "Harga", 120, "e"),
            ("kategori", "Kategori", 120, "center"),
            ("status", "Status", 110, "center"),
            ("fav", "Favorit", 80, "center"),
        ]:
            self.tree.heading(k, text=judul)
            self.tree.column(k, width=lebar, anchor=anchor)
        self.tree.tag_configure("genap", background="#FFFAF0")
        self.tree.tag_configure("habis", foreground=MERAH)

        sb = ttk.Scrollbar(panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=0, column=0, sticky="ew")
        sb.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<Double-1>", lambda e: self._aksi_terpilih(self.toggle_status))

        bawah = tk.Frame(panel, bg=PUTIH)
        bawah.grid(row=1, column=0, columnspan=2, sticky="w", pady=(12, 0))
        for teks, warna, fungsi in [
            (teks_em("❤️", "Favorit"), UNGU, lambda: self._aksi_terpilih(self.toggle_fav)),
            (teks_em("💰", "Ubah Harga"), ORANYE, lambda: self._aksi_terpilih(self.ubah_harga)),
            ("Ubah Status", HIJAU, lambda: self._aksi_terpilih(self.toggle_status)),
            (teks_em("🗑", "Hapus"), MERAH, lambda: self._aksi_terpilih(self.hapus)),
            (teks_em("🔄", "Refresh"), "#8A8A8A", self.muat_ulang),
            ("Menu contoh", "#8A8A8A", self.reset_contoh),
        ]:
            self._tombol(bawah, teks, warna, fungsi).pack(side="left", padx=(0, 8))

    def render_kelola(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for idx, m in enumerate(self.data):
            tags = []
            if idx % 2 == 0:
                tags.append("genap")
            if m.status == "Habis":
                tags.append("habis")
            self.tree.insert("", "end", iid=str(idx), tags=tags,
                             values=(m.nama_menu, m.harga_rupiah(), m.kategori, m.status,
                                     "♥" if m.favorit else ""))

    def _aksi_terpilih(self, fungsi):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Informasi", "Pilih satu menu di tabel terlebih dahulu.")
            return
        fungsi(self.data[int(sel[0])])

    # ------------------------------------------------------------ Aksi data
    def render_semua(self):
        total = len(self.data)
        habis = sum(1 for m in self.data if m.status == "Habis")
        fav = sum(1 for m in self.data if m.favorit)
        self.lbl_stat["total"].config(text=str(total))
        self.lbl_stat["ada"].config(text=str(total - habis))
        self.lbl_stat["habis"].config(text=str(habis))
        self.lbl_stat["fav"].config(text=str(fav))
        self.nav["favorit"].config(text=teks_em("❤️", f"Favorit ({fav})"))

        self.render_beranda()
        self.render_menu()
        self.render_favorit()
        self.render_kelola()

    def simpan_dan_render(self, pesan):
        simpan_data(self.data)
        self.render_semua()
        self.status(pesan)

    def toggle_fav(self, m):
        m.favorit = not m.favorit
        self.simpan_dan_render(
            f"'{m.nama_menu}' masuk favorit." if m.favorit
            else f"'{m.nama_menu}' dihapus dari favorit.")

    def toggle_status(self, m):
        m.status = "Habis" if m.status == "Tersedia" else "Tersedia"
        self.simpan_dan_render(f"Status '{m.nama_menu}' diubah menjadi {m.status}.")

    def ubah_harga(self, m):
        baru = simpledialog.askinteger(
            "Ubah Harga", f"Harga baru untuk {m.nama_menu} (Rp):",
            initialvalue=m.harga_angka(), minvalue=0, parent=self)
        if baru is None:
            return
        m.harga = baru
        self.simpan_dan_render(f"Harga '{m.nama_menu}' diubah menjadi {m.harga_rupiah()}.")

    def hapus(self, m):
        if messagebox.askyesno("Konfirmasi", f"Hapus menu '{m.nama_menu}'?"):
            self.data.remove(m)
            self.simpan_dan_render(f"Menu '{m.nama_menu}' dihapus.")

    def muat_ulang(self):
        self.data = muat_data()
        self.render_semua()
        self.status("Data dimuat ulang dari menu.csv")

    def reset_contoh(self):
        if messagebox.askyesno("Konfirmasi",
                               "Kembalikan semua menu ke data contoh?\n"
                               "Perubahan yang sudah dibuat akan hilang."):
            self.data = contoh_data()
            self.simpan_dan_render("Menu contoh dikembalikan.")


if __name__ == "__main__":
    KantinApp().mainloop()