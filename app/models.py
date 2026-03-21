from datetime import datetime, date
from flask_login import UserMixin
from app import db, login_manager

# Role untuk user
class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nama_lengkap = db.Column(db.String(150), nullable=False)
    nip = db.Column(db.String(50), unique=True)
    aktif = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Pasien Model
class Pasien(db.Model):
    __tablename__ = 'pasien'

    id = db.Column(db.Integer, primary_key=True)
    nik = db.Column(db.String(20), unique=True, nullable=False)
    nama_lengkap = db.Column(db.String(150), nullable=False)
    tanggal_lahir = db.Column(db.Date, nullable=False)
    jenis_kelamin = db.Column(db.String(10), nullable=False)  # L/P
    alamat = db.Column(db.Text)
    no_telepon = db.Column(db.String(20))
    nama_keluarga = db.Column(db.String(150))  # Keluarga yang bisa dihubungi
    no_keluarga = db.Column(db.String(20))
    goldarah = db.Column(db.String(5))  # A, B, AB, O
    alergiobat = db.Column(db.Text)
    # BPJS Fields
    no_bpjs = db.Column(db.String(20))
    kelas_bpjs = db.Column(db.String(10))  # Kelas 1, 2, 3
    status_bpjs = db.Column(db.String(20), default='aktif')  # aktif, nonaktif
    # Faskes
    faskes_tingkat_1 = db.Column(db.String(150))  # Faskes rujukan tingkat 1
    aktif = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Pasien {self.nik} - {self.nama_lengkap}>'

# Poliklinik
class Poliklinik(db.Model):
    __tablename__ = 'poliklinik'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    kode = db.Column(db.String(20), unique=True, nullable=False)
    lantai = db.Column(db.String(20))
    aktif = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Poliklinik {self.nama}>'

# Kamar (untuk rawat inap)
class Kamar(db.Model):
    __tablename__ = 'kamar'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(50), nullable=False)
    kode = db.Column(db.String(20), unique=True, nullable=False)
    kelas = db.Column(db.String(20), nullable=False)  # VIP, I, II, III
    kapasitas = db.Column(db.Integer, default=1)
    tarif = db.Column(db.Numeric(12, 2), default=0)
    lantai = db.Column(db.String(20))
    aktif = db.Column(db.Boolean, default=True)

    tempat_tidur = db.relationship('TempatTidur', backref='kamar', lazy=True)

    def __repr__(self):
        return f'<Kamar {self.kode}>'

class TempatTidur(db.Model):
    __tablename__ = 'tempat_tidur'

    id = db.Column(db.Integer, primary_key=True)
    nomor = db.Column(db.String(10), nullable=False)
    kamar_id = db.Column(db.Integer, db.ForeignKey('kamar.id'), nullable=False)
    status = db.Column(db.String(20), default='tersedia')  # tersedia, occupied, maintenance
    aktif = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<TempatTidur {self.nomor}>'

# Farmasi - Obat
class Obat(db.Model):
    __tablename__ = 'obat'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150), nullable=False)
    kode = db.Column(db.String(20), unique=True)
    jenis = db.Column(db.String(50))  # tablet, kapsul, sirup, injeksi, dll
    dosis = db.Column(db.String(50))
    satuan = db.Column(db.String(20))  # mg, ml, tablet
    stok = db.Column(db.Integer, default=0)
    stok_minimum = db.Column(db.Integer, default=10)
    harga = db.Column(db.Numeric(12, 2), default=0)
    aktif = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Obat {self.nama}>'

# ========== RESEP ==========
class Resep(db.Model):
    __tablename__ = 'resep'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    dokter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='menunggu')  # menunggu, selesai, batal
    catatan = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pasien = db.relationship('Pasien', backref='resep')
    dokter = db.relationship('User', backref='resep')

    def __repr__(self):
        return f'<Resep {self.id}>'

class ResepDetail(db.Model):
    __tablename__ = 'resep_detail'

    id = db.Column(db.Integer, primary_key=True)
    resep_id = db.Column(db.Integer, db.ForeignKey('resep.id'), nullable=False)
    obat_id = db.Column(db.Integer, db.ForeignKey('obat.id'), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)
    dosis = db.Column(db.String(100))  # 3x1, 2x1, dll
    catatan = db.Column(db.Text)

    resep = db.relationship('Resep', backref='details')
    obat = db.relationship('Obat', backref='resep_details')

    def __repr__(self):
        return f'<ResepDetail {self.id}>'

# ========== RAWAT JALAN ==========
class RawatJalan(db.Model):
    __tablename__ = 'rawat_jalan'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    poliklinik_id = db.Column(db.Integer, db.ForeignKey('poliklinik.id'))
    dokter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    nomor_antrian = db.Column(db.Integer, default=1)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    keluhan = db.Column(db.Text)
    diagnose = db.Column(db.Text)
    terapi = db.Column(db.Text)
    status = db.Column(db.String(20), default='menunggu')  # menunggu, diperiksa, selesai
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pasien = db.relationship('Pasien', backref='rawat_jalan')
    poliklinik = db.relationship('Poliklinik', backref='rawat_jalan')
    dokter = db.relationship('User', backref='rawat_jalan')

    def __repr__(self):
        return f'<RawatJalan {self.id} - {self.pasien_id}>'

# ========== RAWAT INAP ==========
class RawatInap(db.Model):
    __tablename__ = 'rawat_inap'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    kamar_id = db.Column(db.Integer, db.ForeignKey('kamar.id'), nullable=False)
    tempat_tidur_id = db.Column(db.Integer, db.ForeignKey('tempat_tidur.id'))
    dokter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tanggal_masuk = db.Column(db.DateTime, default=datetime.utcnow)
    tanggal_keluar = db.Column(db.DateTime)
    diagnosa_masuk = db.Column(db.Text)
    diagnosa_utama = db.Column(db.Text)
    status = db.Column(db.String(20), default='aktif')  # aktif, keluar, meninggal
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pasien = db.relationship('Pasien', backref='rawat_inap')
    kamar = db.relationship('Kamar', backref='rawat_inap')
    tempat_tidur = db.relationship('TempatTidur', backref='rawat_inap')
    dokter = db.relationship('User', backref='rawat_inap')

    def __repr__(self):
        return f'<RawatInap {self.id} - {self.pasien_id}>'

# ========== IGD (INSTALASI GAWAT DARURAT) ==========
class IGD(db.Model):
    __tablename__ = 'igd'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    dokter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    perawat_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    waktu_masuk = db.Column(db.DateTime, default=datetime.utcnow)
    waktu_keluar = db.Column(db.DateTime)
    keluhan_utama = db.Column(db.Text)
    triage = db.Column(db.String(10))  # merah (emergent), kuning (urgent), hijau (stable), hitam (dead)
    diagnose_awal = db.Column(db.Text)
    tindakan = db.Column(db.Text)
    status = db.Column(db.String(20), default='aktif')  # aktif, rawat_inap, pulang, rujuk
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pasien = db.relationship('Pasien', backref='igd')
    dokter = db.relationship('User', foreign_keys=[dokter_id], backref='igd_dokter')
    perawat = db.relationship('User', foreign_keys=[perawat_id], backref='igd_perawat')

    def __repr__(self):
        return f'<IGD {self.id} - {self.pasien_id}>'

# ========== REKAM MEDIS ==========
class RekamMedis(db.Model):
    __tablename__ = 'rekam_medis'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    dokter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    jenis_layanan = db.Column(db.String(50))  # rawat_jalan, rawat_inap, igd
    layanan_id = db.Column(db.Integer)  # ID dari tabel layanan (rawat_jalan, rawat_inap, igd)
    subjective = db.Column(db.Text)  # Keluhan pasien
    objective = db.Column(db.Text)  # Pemeriksaan fisik
    assessment = db.Column(db.Text)  # Diagnose
    plan = db.Column(db.Text)  # Rencana pengobatan
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pasien = db.relationship('Pasien', backref='rekam_medis')
    dokter = db.relationship('User', backref='rekam_medis')

    def __repr__(self):
        return f'<RekamMedis {self.id} - {self.pasien_id}>'

# ========== LABORATORIUM ==========
class JenisPemeriksaan(db.Model):
    __tablename__ = 'jenis_pemeriksaan'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150), nullable=False)
    kode = db.Column(db.String(20), unique=True)
    kategori = db.Column(db.String(50))  # Hematologi, Kimia Klinik, Urinalisa, dll
    harga = db.Column(db.Numeric(12, 2), default=0)
    aktif = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<JenisPemeriksaan {self.nama}>'

class PemeriksaanLab(db.Model):
    __tablename__ = 'pemeriksaan_lab'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    dokter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    nomor_order = db.Column(db.String(20), unique=True)
    tanggal_order = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='menunggu')  # menunggu, diambil, proses, selesai
    diagnosa = db.Column(db.Text)
    catatan = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pasien = db.relationship('Pasien', backref='pemeriksaan_lab')
    dokter = db.relationship('User', backref='pemeriksaan_lab')

    def __repr__(self):
        return f'<PemeriksaanLab {self.id}>'

class PemeriksaanLabDetail(db.Model):
    __tablename__ = 'pemeriksaan_lab_detail'

    id = db.Column(db.Integer, primary_key=True)
    pemeriksaan_id = db.Column(db.Integer, db.ForeignKey('pemeriksaan_lab.id'), nullable=False)
    jenis_pemeriksaan_id = db.Column(db.Integer, db.ForeignKey('jenis_pemeriksaan.id'), nullable=False)
    hasil = db.Column(db.Text)
    nilai_normal = db.Column(db.String(100))
    unit = db.Column(db.String(50))
    status = db.Column(db.String(20), default='menunggu')  # menunggu, proses, selesai
    tanggal_selesai = db.Column(db.DateTime)

    pemeriksaan = db.relationship('PemeriksaanLab', backref='details')
    jenis_pemeriksaan = db.relationship('JenisPemeriksaan', backref='details')

    def __repr__(self):
        return f'<PemeriksaanLabDetail {self.id}>'

# ========== KASIR / BILLING ==========
class Billing(db.Model):
    __tablename__ = 'billing'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    nomor_invoice = db.Column(db.String(20), unique=True)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, lunas, Batal
    subtotal = db.Column(db.Numeric(12, 2), default=0)
    diskon = db.Column(db.Numeric(12, 2), default=0)
    total = db.Column(db.Numeric(12, 2), default=0)
    metode_pembayaran = db.Column(db.String(50))  # cash, debit, kredit, bpjs
    catatan = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pasien = db.relationship('Pasien', backref='billing')

    def __repr__(self):
        return f'<Billing {self.id}>'

class BillingDetail(db.Model):
    __tablename__ = 'billing_detail'

    id = db.Column(db.Integer, primary_key=True)
    billing_id = db.Column(db.Integer, db.ForeignKey('billing.id'), nullable=False)
    layanan = db.Column(db.String(100), nullable=False)  # Rawat Jalan, Rawat Inap, Farmasi, Lab
    item_id = db.Column(db.Integer)  # ID dari layanan terkait
    deskripsi = db.Column(db.Text)
    jumlah = db.Column(db.Integer, default=1)
    harga = db.Column(db.Numeric(12, 2), default=0)
    total_harga = db.Column(db.Numeric(12, 2), default=0)

    billing = db.relationship('Billing', backref='details')

    def __repr__(self):
        return f'<BillingDetail {self.id}>'

class Pembayaran(db.Model):
    __tablename__ = 'pembayaran'

    id = db.Column(db.Integer, primary_key=True)
    billing_id = db.Column(db.Integer, db.ForeignKey('billing.id'), nullable=False)
    jumlah_bayar = db.Column(db.Numeric(12, 2), nullable=False)
    metode = db.Column(db.String(50))
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='sukses')  # sukses, gagal, refund

    billing = db.relationship('Billing', backref='pembayaran')

    def __repr__(self):
        return f'<Pembayaran {self.id}>'

# ========== GUDANG / INVENTARIS ==========
class KategoriBarang(db.Model):
    __tablename__ = 'kategori_barang'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    kode = db.Column(db.String(20), unique=True)
    aktif = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<KategoriBarang {self.nama}>'

class Barang(db.Model):
    __tablename__ = 'barang'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(150), nullable=False)
    kode = db.Column(db.String(20), unique=True)
    kategori_id = db.Column(db.Integer, db.ForeignKey('kategori_barang.id'))
    jenis = db.Column(db.String(50))  # Medis, Non-medis
    stok = db.Column(db.Integer, default=0)
    stok_minimum = db.Column(db.Integer, default=10)
    satuan = db.Column(db.String(20))
    harga_satuan = db.Column(db.Numeric(12, 2), default=0)
    aktif = db.Column(db.Boolean, default=True)

    kategori = db.relationship('KategoriBarang', backref='barang')

    def __repr__(self):
        return f'<Barang {self.nama}>'

class TransaksiStock(db.Model):
    __tablename__ = 'transaksi_stock'

    id = db.Column(db.Integer, primary_key=True)
    barang_id = db.Column(db.Integer, db.ForeignKey('barang.id'), nullable=False)
    jenis = db.Column(db.String(20), nullable=False)  # masuk, keluar
    jumlah = db.Column(db.Integer, nullable=False)
    referensi = db.Column(db.String(100))  # No. PO, No. Resep, dll
    catatan = db.Column(db.Text)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    barang = db.relationship('Barang', backref='transaksi')
    user = db.relationship('User', backref='transaksi_stock')

    def __repr__(self):
        return f'<TransaksiStock {self.id}>'

# ========== ICD-10 (KODING DIAGNOSA) ==========
class ICD10(db.Model):
    __tablename__ = 'icd10'

    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(10), unique=True, nullable=False)
    nama = db.Column(db.String(250), nullable=False)
    kategori = db.Column(db.String(50))  # A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z
    aktif = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<ICD10 {self.kode}>'

# ========== SEP (SURAT ELIGIBILITAS PESERTA) BPJS ==========
class SEP(db.Model):
    __tablename__ = 'sep'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    nomor_sep = db.Column(db.String(20), unique=True)
    tanggal_sep = db.Column(db.DateTime, default=datetime.utcnow)
    faskes_asal = db.Column(db.String(150))  # Faskes rujukan
    diagnosa_awal = db.Column(db.String(250))
    icd10_awal_id = db.Column(db.Integer, db.ForeignKey('icd10.id'))
    kelas_rawat = db.Column(db.String(10))  # Kelas 1, 2, 3
    status = db.Column(db.String(20), default='aktif')  # aktif, digunakan, expired
    referensi = db.Column(db.String(50))  # No. Rujukan
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pasien = db.relationship('Pasien', backref='sep')
    diagnosa_awal_icd = db.relationship('ICD10', backref='sep_diagnosa')

    def __repr__(self):
        return f'<SEP {self.nomor_sep}>'

# ========== RUJUKAN (REFERAL) ==========
class Rujukan(db.Model):
    __tablename__ = 'rujukan'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    sep_id = db.Column(db.Integer, db.ForeignKey('sep.id'))
    nomor_rujukan = db.Column(db.String(30), unique=True)
    tanggal_rujukan = db.Column(db.DateTime, default=datetime.utcnow)
    faskes_tujuan = db.Column(db.String(150))  # RS tujuan
    faskes_asal = db.Column(db.String(150))  # Dari faskes mana
    diagnosa = db.Column(db.String(250))
    icd10_id = db.Column(db.Integer, db.ForeignKey('icd10.id'))
    catatan = db.Column(db.Text)
    status = db.Column(db.String(20), default='aktif')  # aktif, digunakan, expired, batal
    jenis_rujukan = db.Column(db.String(20), default='keluar')  # masuk/keluar
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pasien = db.relationship('Pasien', backref='rujukan')
    sep = db.relationship('SEP', backref='rujukan')
    icd10 = db.relationship('ICD10', backref='rujukan')

    def __repr__(self):
        return f'<Rujukan {self.nomor_rujukan}>'

# ========== KLAIM BPJS ==========
class Klaim(db.Model):
    __tablename__ = 'klaim'

    id = db.Column(db.Integer, primary_key=True)
    nomor_klaim = db.Column(db.String(30), unique=True)
    periode_awal = db.Column(db.Date)
    periode_akhir = db.Column(db.Date)
    total_tarif = db.Column(db.Numeric(15, 2), default=0)
    status_klaim = db.Column(db.String(20), default='draft')  # draft, submitted, verifikasi, paid, rejected
    tanggal_submit = db.Column(db.DateTime)
    tanggal_bayar = db.Column(db.DateTime)
    catatan = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Klaim {self.nomor_klaim}>'

class KlaimDetail(db.Model):
    __tablename__ = 'klaim_detail'

    id = db.Column(db.Integer, primary_key=True)
    klaim_id = db.Column(db.Integer, db.ForeignKey('klaim.id'), nullable=False)
    sep_id = db.Column(db.Integer, db.ForeignKey('sep.id'))
    diagnose = db.Column(db.String(250))
    icd10_id = db.Column(db.Integer, db.ForeignKey('icd10.id'))
    prosedur = db.Column(db.String(250))
    icd9_id = db.Column(db.Integer)
    tarif = db.Column(db.Numeric(15, 2), default=0)

    klaim = db.relationship('Klaim', backref='details')
    sep = db.relationship('SEP', backref='klaim_details')
    icd10 = db.relationship('ICD10', backref='klaim_details')

    def __repr__(self):
        return f'<KlaimDetail {self.id}>'

# ========== INA-CBGs (KODE TARIF BPJS) ==========
class INACBGs(db.Model):
    __tablename__ = 'inacbgs'

    id = db.Column(db.Integer, primary_key=True)
    kode_cbg = db.Column(db.String(20), unique=True, nullable=False)
    nama_cbg = db.Column(db.String(250), nullable=False)
    tarif = db.Column(db.Numeric(15, 2), default=0)
    kategori = db.Column(db.String(50))  # bedah, non-bedah, k煽ong, ibu
    sub_kategori = db.Column(db.String(50))
    aktif = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<INACBGs {self.kode_cbg}>'

# ========== ICD-9 CM (KODE TINDAKAN) ==========
class ICD9(db.Model):
    __tablename__ = 'icd9'

    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(10), unique=True, nullable=False)
    nama = db.Column(db.String(250), nullable=False)
    kategori = db.Column(db.String(50))  # tindakan, operasi, diagnostik
    aktif = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<ICD9 {self.kode}>'

# ========== RESUME MEDIS ==========
class ResumeMedis(db.Model):
    __tablename__ = 'resume_medis'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    layanan_jenis = db.Column(db.String(20))  # rawat_inap, igd
    layanan_id = db.Column(db.Integer)
    tanggal_masuk = db.Column(db.Date)
    tanggal_keluar = db.Column(db.Date)
    diagnosa_utama = db.Column(db.Text)
    diagnosa_sekunder = db.Column(db.Text)
    prosedur = db.Column(db.Text)
    icd9_ids = db.Column(db.String(100))  # Comma-separated ICD-9 IDs
    kondisi_keluar = db.Column(db.String(30))  # sembuh, pulang, rujuk, meninggal
    obat_pulang = db.Column(db.Text)
    kontrol_ulang = db.Column(db.Text)
    dokter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pasien = db.relationship('Pasien', backref='resume_medis')
    dokter = db.relationship('User', backref='resume_medis')

    def __repr__(self):
        return f'<ResumeMedis {self.id} - {self.pasien_id}>'

# ========== SURAT KETERANGAN SAKIT ==========
class SuratSakit(db.Model):
    __tablename__ = 'surat_sakit'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    tanggal_surat = db.Column(db.Date, default=datetime.utcnow().date())
    diagnosa = db.Column(db.Text)
    lama_sakit = db.Column(db.Integer)  # hari
    mulai_tanggal = db.Column(db.Date)
    sampai_tanggal = db.Column(db.Date)
    dokter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    catatan = db.Column(db.Text)
    status = db.Column(db.String(20), default='aktif')  # aktif, used

    pasien = db.relationship('Pasien', backref='surat_sakit')
    dokter = db.relationship('User', backref='surat_sakit')

    def __repr__(self):
        return f'<SuratSakit {self.id}>'

# ========== CONSENT (SETUJU TINDAKAN) ==========
class Consent(db.Model):
    __tablename__ = 'consent'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    tindakan = db.Column(db.String(200), nullable=False)
    tanggal_consent = db.Column(db.DateTime, default=datetime.utcnow)
    dokter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='granted')  # granted, denied, revoked
    catatan = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pasien = db.relationship('Pasien', backref='consent')
    dokter = db.relationship('User', backref='consent')

    def __repr__(self):
        return f'<Consent {self.id}>'

# ========== JADWAL DOKTER ==========
class JadwalDokter(db.Model):
    __tablename__ = 'jadwal_dokter'

    id = db.Column(db.Integer, primary_key=True)
    dokter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    poliklinik_id = db.Column(db.Integer, db.ForeignKey('poliklinik.id'), nullable=False)
    hari = db.Column(db.String(20), nullable=False)  # Senin, Selasa, etc
    jam_mulai = db.Column(db.Time)
    jam_selesai = db.Column(db.Time)
    kapasitas = db.Column(db.Integer, default=20)  # max pasien/hari
    aktif = db.Column(db.Boolean, default=True)

    dokter = db.relationship('User', backref='jadwal_dokter')
    poliklinik = db.relationship('Poliklinik', backref='jadwal_dokter')

    def __repr__(self):
        return f'<JadwalDokter {self.dokter_id} - {self.hari}>'


# ========== RADIOLOGI ==========
class JenisPemeriksaanRadiologi(db.Model):
    __tablename__ = 'jenis_pemeriksaan_radiologi'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)  # CT Scan, MRI, USG, Rontgen
    kategori = db.Column(db.String(50))  # radiologi_diagnostik, radiologi_intervensional
    deskripsi = db.Column(db.Text)
    aktif = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<JenisPemeriksaanRadiologi {self.nama}>'


class PemeriksaanRadiologi(db.Model):
    __tablename__ = 'pemeriksaan_radiologi'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    no_order = db.Column(db.String(50), unique=True)
    tanggal_order = db.Column(db.DateTime, default=datetime.now)
    dokter_pengirim_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='menunggu')  # menunggu, diambil, proses, selesai
    catatan = db.Column(db.Text)

    pasien = db.relationship('Pasien', backref='pemeriksaan_radiologi')
    dokter_pengirim = db.relationship('User', backref='order_radiologi')
    details = db.relationship('PemeriksaanRadiologiDetail', backref='pemeriksaan', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<PemeriksaanRadiologi {self.no_order}>'


class PemeriksaanRadiologiDetail(db.Model):
    __tablename__ = 'pemeriksaan_radiologi_detail'

    id = db.Column(db.Integer, primary_key=True)
    pemeriksaan_radiologi_id = db.Column(db.Integer, db.ForeignKey('pemeriksaan_radiologi.id'), nullable=False)
    jenis_pemeriksaan_id = db.Column(db.Integer, db.ForeignKey('jenis_pemeriksaan_radiologi.id'), nullable=False)
    hasil = db.Column(db.Text)
    gambar_path = db.Column(db.String(255))
    tanggal_selesai = db.Column(db.DateTime)
    teknisi_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    jenis_pemeriksaan = db.relationship('JenisPemeriksaanRadiologi')
    teknisi = db.relationship('User', backref='pemeriksaan_radiologi_teknisi')

    def __repr__(self):
        return f'<PemeriksaanRadiologiDetail {self.id}>'


# ========== BANK DARAH ==========
class GolonganDarah(db.Model):
    __tablename__ = 'golongan_darah'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(5), nullable=False)  # A, B, AB, O
    faktor_rhesus = db.Column(db.String(10))  # positif, negatif
    aktif = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<GolonganDarah {self.nama}{self.faktor_rhesus}>'


class StokDarah(db.Model):
    __tablename__ = 'stok_darah'

    id = db.Column(db.Integer, primary_key=True)
    gol_darah_id = db.Column(db.Integer, db.ForeignKey('golongan_darah.id'), nullable=False)
    komponen = db.Column(db.String(50))  # WB, PRC, TC, FFP, Cryo
    jumlah = db.Column(db.Integer, default=0)  # kantong
    expire_date = db.Column(db.Date)
    tanggal_masuk = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(20), default='tersedia')  # tersedia, kedaluwarsa, digunakan

    gol_darah = db.relationship('GolonganDarah', backref='stok_darah')

    def __repr__(self):
        return f'<StokDarah {self.gol_darah.nama} {self.komponen}>'


class Pendonor(db.Model):
    __tablename__ = 'pendonor'

    id = db.Column(db.Integer, primary_key=True)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    gol_darah_id = db.Column(db.Integer, db.ForeignKey('golongan_darah.id'))
    tanggal_lahir = db.Column(db.Date)
    jk = db.Column(db.String(1))  # L, P
    alamat = db.Column(db.Text)
    no_telepon = db.Column(db.String(20))
    terakhir_donor = db.Column(db.Date)
    aktif = db.Column(db.Boolean, default=True)

    gol_darah = db.relationship('GolonganDarah', backref='pendonor')

    def __repr__(self):
        return f'<Pendonor {self.nama_lengkap}>'


class PermintaanDarah(db.Model):
    __tablename__ = 'permintaan_darah'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    gol_darah_id = db.Column(db.Integer, db.ForeignKey('golongan_darah.id'), nullable=False)
    komponen = db.Column(db.String(50))
    jumlah = db.Column(db.Integer, default=1)
    dokter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tanggal_permintaan = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='menunggu')  # menunggu, disetujui, ditolak, diberikan
    catatan = db.Column(db.Text)

    pasien = db.relationship('Pasien', backref='permintaan_darah')
    gol_darah = db.relationship('GolonganDarah', backref='permintaan_darah')
    dokter = db.relationship('User', backref='permintaan_darah')

    def __repr__(self):
        return f'<PermintaanDarah {self.id}>'


class TransaksiDarah(db.Model):
    __tablename__ = 'transaksi_darah'

    id = db.Column(db.Integer, primary_key=True)
    stok_darah_id = db.Column(db.Integer, db.ForeignKey('stok_darah.id'), nullable=False)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    permintaan_id = db.Column(db.Integer, db.ForeignKey('permintaan_darah.id'))
    tanggal_transfusi = db.Column(db.DateTime, default=datetime.now)
    dokter_pemeriksa_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    stok_darah = db.relationship('StokDarah', backref='transaksi_darah')
    pasien = db.relationship('Pasien', backref='transaksi_darah')
    permintaan = db.relationship('PermintaanDarah', backref='transaksi_darah')
    dokter = db.relationship('User', backref='transaksi_darah')

    def __repr__(self):
        return f'<TransaksiDarah {self.id}>'


# ========== OK (OPERATING ROOM) ==========
class KamarOK(db.Model):
    __tablename__ = 'kamar_ok'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(50), nullable=False)  # OK 1, OK 2
    lokasi = db.Column(db.String(100))
    kapasitas = db.Column(db.Integer, default=1)
    peralatan = db.Column(db.Text)
    aktif = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<KamarOK {self.nama}>'


class Operasi(db.Model):
    __tablename__ = 'operasi'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    no_operasi = db.Column(db.String(50), unique=True)
    tanggal_operasi = db.Column(db.DateTime)
    diagnosis = db.Column(db.Text)
    prosedur = db.Column(db.Text)  # ICD-9
    dokter_surgeon_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    dokter_anestesi_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='terjadwal')  # terjadwal, proses, selesai, batal
    catatan = db.Column(db.Text)

    pasien = db.relationship('Pasien', backref='operasi')
    dokter_surgeon = db.relationship('User', foreign_keys=[dokter_surgeon_id], backref='operasi_surgeon')
    dokter_anestesi = db.relationship('User', foreign_keys=[dokter_anestesi_id], backref='operasi_anestesi')
    jadwal = db.relationship('JadwalOK', backref='operasi', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Operasi {self.no_operasi}>'


class JadwalOK(db.Model):
    __tablename__ = 'jadwal_ok'

    id = db.Column(db.Integer, primary_key=True)
    operasi_id = db.Column(db.Integer, db.ForeignKey('operasi.id'), nullable=False)
    kamar_ok_id = db.Column(db.Integer, db.ForeignKey('kamar_ok.id'), nullable=False)
    tanggal = db.Column(db.Date)
    jam_mulai = db.Column(db.Time)
    jam_selesai = db.Column(db.Time)
    status = db.Column(db.String(20), default='terjadwal')  # terjadwal, berlangsung, selesai, batal

    kamar_ok = db.relationship('KamarOK', backref='jadwal_ok')

    def __repr__(self):
        return f'<JadwalOK {self.tanggal}>'


# ========== VK (VERLOS KAMER - KAMAR BERSALIN) ==========
class KamarVK(db.Model):
    __tablename__ = 'kamar_vk'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(50), nullable=False)  # VK 1, VK 2, VK 3
    kapasitas = db.Column(db.Integer, default=1)
    fasilitas = db.Column(db.Text)  # alat melahirkan, infant warmer, dll
    status = db.Column(db.String(20), default='tersedia')  # tersedia, occupied, cleaning
    aktif = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<KamarVK {self.nama}>'


class RegistrasiKehilangan(db.Model):
    __tablename__ = 'registrasi_kehajibanjembatan'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    no_registrasi = db.Column(db.String(50), unique=True)
    tanggal_registrasi = db.Column(db.Date, default=date.today)
    taksiran_persalinan = db.Column(db.Date)
    risiko_kehamilan = db.Column(db.String(20))  # rendah, tinggi
    tenaga_penolong = db.Column(db.String(50))  # bidan, dokter
    aktif = db.Column(db.Boolean, default=True)

    pasien = db.relationship('Pasien', backref='registrasi_kehamilan')
    pemeriksaan = db.relationship('PemeriksaanKehilangan', backref='registrasi_kehamili', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<RegistrasiKehilangan {self.no_registrasi}>'


class PemeriksaanKehilangan(db.Model):
    __tablename__ = 'pemeriksaan_kehamilan'

    id = db.Column(db.Integer, primary_key=True)
    registrasi_kehajibanjembatan_id = db.Column(db.Integer, db.ForeignKey('registrasi_kehajibanjembatan.id'), nullable=False)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    tanggal_periksa = db.Column(db.DateTime, default=datetime.now)
    trimester = db.Column(db.Integer)  # 1, 2, 3
    berat_badan = db.Column(db.Numeric(5,2))
    tekanan_darah = db.Column(db.String(20))
    tinggi_fundus = db.Column(db.Numeric(5,2))
    detak_jantung_janin = db.Column(db.Integer)
    diagnosis = db.Column(db.Text)
    catatan = db.Column(db.Text)

    pasien = db.relationship('Pasien', backref='pemeriksaan_kehamilan')

    def __repr__(self):
        return f'<PemeriksaanKehilangan {self.id}>'


class Persalinan(db.Model):
    __tablename__ = 'persalinan'

    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.id'), nullable=False)
    no_persalinan = db.Column(db.String(50), unique=True)
    tanggal_masuk = db.Column(db.DateTime)
    tanggal_persalinan = db.Column(db.DateTime)
    kamar_vk_id = db.Column(db.Integer, db.ForeignKey('kamar_vk.id'))
    jenis_persalinan = db.Column(db.String(30))  # normal, sectio_caesarea, water_birth
    diagnosis = db.Column(db.Text)
    dokter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bidan_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    kondisi_ibu = db.Column(db.String(20))  # sehat, komplikasi, meninggal
    kondisi_bayi = db.Column(db.String(20))  # sehat, komplikasi, meninggal
    berat_bayi = db.Column(db.Numeric(5,2))  # gram
    jk_bayi = db.Column(db.String(1))  # L, P
    status = db.Column(db.String(20), default='dalam_proses')  # dalam_proses, selesai, rujuk
    catatan = db.Column(db.Text)

    pasien = db.relationship('Pasien', backref='persalinan')
    kamar_vk = db.relationship('KamarVK', backref='persalinan')
    dokter = db.relationship('User', foreign_keys=[dokter_id], backref='persalinan_dokter')
    bidan = db.relationship('User', foreign_keys=[bidan_id], backref='persalinan_bidan')

    def __repr__(self):
        return f'<Persalinan {self.no_persalinan}>'


# ========== BED MANAGEMENT ==========
# TempatTidur sudah ada, perlu tambah field extension
