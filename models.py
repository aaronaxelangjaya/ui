class Menu:
    def __init__(self, nama_menu, harga, kategori, status="Tersedia", favorit=False):
        self.nama_menu = nama_menu
        self.harga = harga
        self.kategori = kategori
        self.status = status
        self.favorit = favorit

    def to_list(self):
        return [
            self.nama_menu,
            self.harga,
            self.kategori,
            self.status,
            "Ya" if self.favorit else "Tidak",
        ]

    def harga_angka(self):
        try:
            return int(self.harga)
        except (ValueError, TypeError):
            return 0

    def harga_rupiah(self):
        try:
            return "Rp " + f"{int(self.harga):,}".replace(",", ".")
        except (ValueError, TypeError):
            return str(self.harga)

    def __str__(self):
        return f"{self.nama_menu} - Rp{self.harga} ({self.kategori}) - {self.status}"