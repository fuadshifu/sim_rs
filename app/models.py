from datetime import datetime
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
