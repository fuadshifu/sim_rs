"""
Script untuk inisialisasi database awal
Menambahkan roles dan user admin default
"""

from app import create_app, db, bcrypt
from app.models import Role, User, Poliklinik, Kamar, TempatTidur, Obat, ICD10, ICD9, INACBGs

def init_db():
    app = create_app('development')

    with app.app_context():
        # Drop and create all tables
        db.drop_all()
        db.create_all()

        # Create Roles
        roles = [
            Role(name='admin', description='Administrator sistem'),
            Role(name='dokter', description='Dokter'),
            Role(name='perawat', description='Perawat'),
            Role(name='apoteker', description='Apoteker'),
            Role(name='kasir', description='Kasir'),
            Role(name='pendaftaran', description='Petugas Pendaftaran'),
        ]

        for role in roles:
            db.session.add(role)

        db.session.commit()

        # Create Admin User
        admin_role = Role.query.filter_by(name='admin').first()
        admin_password = bcrypt.generate_password_hash('admin123').decode('utf-8')

        admin = User(
            username='admin',
            email='admin@simrs.local',
            password_hash=admin_password,
            nama_lengkap='Administrator',
            nip='123456789',
            role_id=admin_role.id,
            aktif=True
        )

        db.session.add(admin)

        # Create Poliklinik
        poliklinik_list = [
            Poliklinik(nama='Poli Umum', kode='POLI-001', lantai='Lantai 1'),
            Poliklinik(nama='Poli Gigi', kode='POLI-002', lantai='Lantai 1'),
            Poliklinik(nama='Poli Anak', kode='POLI-003', lantai='Lantai 2'),
            Poliklinik(nama='Poli Kandungan', kode='POLI-004', lantai='Lantai 2'),
            Poliklinik(nama='Poli Bedah', kode='POLI-005', lantai='Lantai 3'),
            Poliklinik(nama='Poli Mata', kode='POLI-006', lantai='Lantai 3'),
            Poliklinik(nama='Poli THT', kode='POLI-007', lantai='Lantai 3'),
            Poliklinik(nama='Poli Kulit', kode='POLI-008', lantai='Lantai 4'),
        ]

        for poli in poliklinik_list:
            db.session.add(poli)

        db.session.commit()

        # Create Kamar
        kamar_list = [
            Kamar(nama='Kamar VIP 1', kode='VIP-001', kelas='VIP', kapasitas=1, tarif=500000),
            Kamar(nama='Kamar VIP 2', kode='VIP-002', kelas='VIP', kapasitas=1, tarif=500000),
            Kamar(nama='Kamar Kelas I A', kode='KI-001', kelas='I', kapasitas=2, tarif=250000),
            Kamar(nama='Kamar Kelas I B', kode='KI-002', kelas='I', kapasitas=2, tarif=250000),
            Kamar(nama='Kamar Kelas II A', kode='KII-001', kelas='II', kapasitas=3, tarif=150000),
            Kamar(nama='Kamar Kelas II B', kode='KII-002', kelas='II', kapasitas=3, tarif=150000),
            Kamar(nama='Kamar Kelas III A', kode='KIII-001', kelas='III', kapasitas=4, tarif=75000),
            Kamar(nama='Kamar Kelas III B', kode='KIII-002', kelas='III', kapasitas=4, tarif=75000),
        ]

        for kamar in kamar_list:
            db.session.add(kamar)

        db.session.commit()

        # Create Tempat Tidur
        kamar_id_map = {k.kode: k.id for k in Kamar.query.all()}
        tt_data = [
            ('VIP-001', ['01']), ('VIP-002', ['01']),
            ('KI-001', ['01', '02']), ('KI-002', ['01', '02']),
            ('KII-001', ['01', '02', '03']), ('KII-002', ['01', '02', '03']),
            ('KIII-001', ['01', '02', '03', '04']), ('KIII-002', ['01', '02', '03', '04']),
        ]

        for kode, nomor_list in tt_data:
            for nomor in nomor_list:
                tt = TempatTidur(
                    nomor=nomor,
                    kamar_id=kamar_id_map[kode],
                    status='tersedia'
                )
                db.session.add(tt)

        db.session.commit()

        # Create Sample Obat
        obat_list = [
            Obat(nama='Paracetamol 500mg', kode='OBT-001', jenis='Tablet', dosis='500mg', satuan='tablet', stok=1000, stok_minimum=100, harga=100),
            Obat(nama='Amoxicillin 500mg', kode='OBT-002', jenis='Kapsul', dosis='500mg', satuan='kapsul', stok=500, stok_minimum=50, harga=250),
            Obat(nama='Ibuprofen 400mg', kode='OBT-003', jenis='Tablet', dosis='400mg', satuan='tablet', stok=800, stok_minimum=100, harga=150),
            Obat(nama='Omeprazole 20mg', kode='OBT-004', jenis='Kapsul', dosis='20mg', satuan='kapsul', stok=300, stok_minimum=30, harga=500),
            Obat(nama='Salbutamol 4mg', kode='OBT-005', jenis='Tablet', dosis='4mg', satuan='tablet', stok=200, stok_minimum=20, harga=200),
            Obat(nama='Cetirizine 10mg', kode='OBT-006', jenis='Tablet', dosis='10mg', satuan='tablet', stok=500, stok_minimum=50, harga=150),
            Obat(nama='Metronidazole 500mg', kode='OBT-007', jenis='Tablet', dosis='500mg', satuan='tablet', stok=400, stok_minimum=40, harga=300),
            Obat(nama='Risperidone 2mg', kode='OBT-008', jenis='Tablet', dosis='2mg', satuan='tablet', stok=10, stok_minimum=20, harga=1000),  # Low stock
        ]

        for obat in obat_list:
            db.session.add(obat)

        db.session.commit()

        # Create Sample ICD-10 Codes
        icd10_list = [
            # A - Infeksi
            ICD10(kode='A00', nama='Kolera', kategori='A'),
            ICD10(kode='A01', nama='Demam Tifoid dan Paratifoid', kategori='A'),
            ICD10(kode='A02', nama='Infeksi Salmonella lain', kategori='A'),
            ICD10(kode='A03', nama='Shigellosis', kategori='A'),
            ICD10(kode='A04', nama='Infeksi Bakteri Usus Lain', kategori='A'),
            ICD10(kode='A05', nama='Keracunan Makanan Bakteri', kategori='A'),
            ICD10(kode='A09', nama='Gastroenteritis dan Kolitis Infeksius', kategori='A'),

            # B - Infeksi
            ICD10(kode='B00', nama='Infeksi Virus Herpes', kategori='B'),
            ICD10(kode='B01', nama='Cacar Air [Varisela]', kategori='B'),
            ICD10(kode='B05', nama='Campak', kategori='B'),
            ICD10(kode='B06', nama='Rubella', kategori='B'),
            ICD10(kode='B18', nama='Hepatitis Virus Kronis', kategori='B'),
            ICD10(kode='B20', nama='Penyakit Virus HIV', kategori='B'),
            ICD10(kode='B25', nama='Penyakit Virus Sitomegal', kategori='B'),
            ICD10(kode='B34', nama='Infeksi Virus, tidak spesifik', kategori='B'),

            # C - Neoplasma
            ICD10(kode='C00', nama='Neoplasma Jinak Bibir', kategori='C'),
            ICD10(kode='C11', nama='Neoplasma Jinak Nasofaring', kategori='C'),
            ICD10(kode='C34', nama='Neoplasma Jinak Bronkus dan Paru', kategori='C'),
            ICD10(kode='C50', nama='Neoplasma Jinak Payudara', kategori='C'),
            ICD10(kode='C56', nama='Neoplasma Jinak Ovarium', kategori='C'),
            ICD10(kode='C61', nama='Neoplasma Jinak Prostat', kategori='C'),

            # D - Darah
            ICD10(kode='D50', nama='Defisiensi Besi Anemia', kategori='D'),
            ICD10(kode='D51', nama='Defisiensi Vitamin B12 Anemia', kategori='D'),
            ICD10(kode='D64', nama='Anemia Lainnya', kategori='D'),
            ICD10(kode='D65', nama='Purpura Demam Berdarah', kategori='D'),
            ICD10(kode='D68', nama='Purpura dan Kondisi Hemoragik Lain', kategori='D'),
            ICD10(kode='D69', nama='Purpura dan Kondisi Hemoragik Lainnya', kategori='D'),

            # E - Endokrin
            ICD10(kode='E10', nama='Diabetes Mellitus Tipe I', kategori='E'),
            ICD10(kode='E11', nama='Diabetes Mellitus Tipe II', kategori='E'),
            ICD10(kode='E13', nama='Diabetes Mellitus Lainnya', kategori='E'),
            ICD10(kode='E16', nama='Gangguan Kelenjar Endokrin Lain', kategori='E'),
            ICD10(kode='E44', nama='Protein-Energy Malnutrisi', kategori='E'),
            ICD10(kode='E53', nama='Defisiensi Vitamin B', kategori='E'),
            ICD10(kode='E66', nama='Obesitas', kategori='E'),

            # F - Jiwa
            ICD10(kode='F10', nama='Gangguan Mental dan Perilaku Akibat Alkohol', kategori='F'),
            ICD10(kode='F20', nama='Skizofrenia', kategori='F'),
            ICD10(kode='F32', nama='Episode Depresif', kategori='F'),
            ICD10(kode='F41', nama='Gangguan Kecemasan', kategori='F'),
            ICD10(kode='F51', nama='Gangguan Tidur Non-Organik', kategori='F'),
            ICD10(kode='F70', nama='Retardasi Mental Ringan', kategori='F'),
            ICD10(kode='F79', nama='Retardasi Mental Tidak Spec', kategori='F'),

            # G - Saraf
            ICD10(kode='G00', nama='Meningitis Bakteri', kategori='G'),
            ICD10(kode='G03', nama='Meningitis Lain dan Tidak Spec', kategori='G'),
            ICD10(kode='G20', nama='Penyakit Parkinson', kategori='G'),
            ICD10(kode='G30', nama='Penyakit Alzheimer', kategori='G'),
            ICD10(kode='G40', nama='Epilepsi', kategori='G'),
            ICD10(kode='G43', nama='Migren', kategori='G'),
            ICD10(kode='G44', nama='Sindrom Sakit Kepala Lain', kategori='G'),
            ICD10(kode='G50', nama='Gangguan Saraf Kranial', kategori='G'),
            ICD10(kode='G80', nama='Cerebral Palsy', kategori='G'),
            ICD10(kode='G90', nama='Gangguan Sistem Saraf Otonom', kategori='G'),

            # H - Mata
            ICD10(kode='H00', nama='Hordeolum dan Kalazion', kategori='H'),
            ICD10(kode='H10', nama='Konjungtivitis', kategori='H'),
            ICD10(kode='H16', nama='Keratitis', kategori='H'),
            ICD10(kode='H25', nama='Katarak Senilis', kategori='H'),
            ICD10(kode='H26', nama='Katarak Lainnya', kategori='H'),
            ICD10(kode='H40', nama='Glaukoma', kategori='H'),
            ICD10(kode='H50', nama='Strabismus', kategori='H'),
            ICD10(kode='H52', nama='Gangguan Refraksi dan Akomodasi', kategori='H'),

            # I - Jantung
            ICD10(kode='I10', nama='Hipertensi Esensial', kategori='I'),
            ICD10(kode='I20', nama='Angina Pectoris', kategori='I'),
            ICD10(kode='I21', nama='Infark Miokard Akut', kategori='I'),
            ICD10(kode='I24', nama='Penyakit Jantung Iskemik Akut Lain', kategori='I'),
            ICD10(kode='I25', nama='Penyakit Jantung Iskemik Kronis', kategori='I'),
            ICD10(kode='I48', nama='Fibrilasi dan Flutter Atrial', kategori='I'),
            ICD10(kode='I50', nama='Gagal Jantung', kategori='I'),
            ICD10(kode='I63', nama='Stroke Non-Hemoragik', kategori='I'),
            ICD10(kode='I64', nama='Stroke, Tidak Spec sebagai Hemoragik atau Infark', kategori='I'),

            # J - Saluran Napas
            ICD10(kode='J00', nama='Nasofaringitis Akut [Pilek]', kategori='J'),
            ICD10(kode='J01', nama='Sinusitis Akut', kategori='J'),
            ICD10(kode='J03', nama='Tonsilitis Akut', kategori='J'),
            ICD10(kode='J06', nama='Infeksi Saluran Pernapasan Akut Multipel', kategori='J'),
            ICD10(kode='J12', nama='Pneumonia Virus', kategori='J'),
            ICD10(kode='J18', nama='Pneumonia, Organisme Tidak Spec', kategori='J'),
            ICD10(kode='J44', nama='Penyakit Paru Obstruktif Kronik', kategori='J'),
            ICD10(kode='J45', nama='Asma', kategori='J'),
            ICD10(kode='J96', nama='Gangguan Pernapasan', kategori='J'),

            # K - Pencernaan
            ICD10(kode='K01', nama='Gingivitis dan Penyakit Periodontal', kategori='K'),
            ICD10(kode='K02', nama='Karies Gigi', kategori='K'),
            ICD10(kode='K03', nama='Penyakit Jaringan Keras Gigi Lain', kategori='K'),
            ICD10(kode='K08', nama='Gangguan Gigi dan Struktur Pendukung Lain', kategori='K'),
            ICD10(kode='K25', nama='Ulkus Lambung', kategori='K'),
            ICD10(kode='K26', nama='Ulkus Duodenum', kategori='K'),
            ICD10(kode='K29', nama='Gastritis dan Duodenitis', kategori='K'),
            ICD10(kode='K35', nama='Apendisitis Akut', kategori='K'),
            ICD10(kode='K36', nama='Apendisitis Lainnya', kategori='K'),
            ICD10(kode='K40', nama='Hernia Inguinal', kategori='K'),
            ICD10(kode='K56', nama=' Ileus Paralitik', kategori='K'),
            ICD10(kode='K70', nama='Penyakit Alkoholik Hati', kategori='K'),
            ICD10(kode='K80', nama='Kolelitiasis', kategori='K'),
            ICD10(kode='K85', nama='Pankreatitis Akut', kategori='K'),

            # L - Kulit
            ICD10(kode='L00', nama='Infeksi Kulit Stafilokokus', kategori='L'),
            ICD10(kode='L01', nama='Impetigo', kategori='L'),
            ICD10(kode='L02', nama='Pioderma Lokal', kategori='L'),
            ICD10(kode='L23', nama='Dermatitis Alergik Kontak', kategori='L'),
            ICD10(kode='L30', nama='Dermatitis Tidak Spec', kategori='L'),
            ICD10(kode='L50', nama='Urtikaria', kategori='L'),
            ICD10(kode='L70', nama='Akne', kategori='L'),

            # M - Tulang
            ICD10(kode='M00', nama='Artritis Piogenik', kategori='M'),
            ICD10(kode='M13', nama='Artritis Lainnya', kategori='M'),
            ICD10(kode='M17', nama='Osteoartritis Gonartrosis', kategori='M'),
            ICD10(kode='M25', nama='Gangguan Sendi, Tidak Spec', kategori='M'),
            ICD10(kode='M54', nama='Dorsoalgia', kategori='M'),
            ICD10(kode='M75', nama='Lesi Bahu', kategori='M'),
            ICD10(kode='M79', nama='Gangguan Jaringan Lunak', kategori='M'),

            # N - Ginjal
            ICD10(kode='N00', nama='Sindrom Nefritik Akut', kategori='N'),
            ICD10(kode='N04', nama='Sindrom Nefrotik', kategori='N'),
            ICD10(kode='N10', nama='Pielonefritis Akut', kategori='N'),
            ICD10(kode='N11', nama='Pielonefritis Kronis', kategori='N'),
            ICD10(kode='N17', nama='Gagal Ginjal Akut', kategori='N'),
            ICD10(kode='N18', nama='Gagal Ginjal Kronis', kategori='N'),
            ICD10(kode='N39', nama='Gangguan Sistem Kemih Lain', kategori='N'),

            # O - Obstetri
            ICD10(kode='O00', nama='Kehamiln Ektopik', kategori='O'),
            ICD10(kode='O20', nama='Perdarahan Dini Kehamilan', kategori='O'),
            ICD10(kode='O24', nama='Diabetes Mellitus pada Kehamilan', kategori='O'),
            ICD10(kode='O32', nama='Pemantauan Kehilangan Gizi', kategori='O'),
            ICD10(kode='O44', nama='Plasenta Previa', kategori='O'),
            ICD10(kode='O45', nama='Solusio Plasenta', kategori='O'),
            ICD10(kode='O63', nama='Persalinan Lama', kategori='O'),
            ICD10(kode='O70', nama='Laserasi Saat Persalinan', kategori='O'),
            ICD10(kode='O72', nama='Perdarahan Postpartum', kategori='O'),
            ICD10(kode='O80', nama='Persalinan Tunggal Spontan', kategori='O'),

            # R - Gejala
            ICD10(kode='R05', nama='Batuk', kategori='R'),
            ICD10(kode='R10', nama='Nyeri Abdomen dan Panggul', kategori='R'),
            ICD10(kode='R11', nama='Mual dan Muntah', kategori='R'),
            ICD10(kode='R18', nama='Asites', kategori='R'),
            ICD10(kode='R21', nama='Ruam dan Erupsi Tidak Spec', kategori='R'),
            ICD10(kode='R50', nama='Demam Tidak Spec', kategori='R'),
            ICD10(kode='R51', nama='Sakit Kepala', kategori='R'),
            ICD10(kode='R52', nama='Nyeri, Tidak Spec', kategori='R'),
            ICD10(kode='R55', nama='Sinkop dan Kolaps', kategori='R'),
            ICD10(kode='R57', nama='Syok, Tidak Spec', kategori='R'),
            ICD10(kode='R94', nama='Hasil Investigasi Diagnostik Abnormal', kategori='R'),

            # S - Trauma
            ICD10(kode='S00', nama='Cedera Kepala Superfisial', kategori='S'),
            ICD10(kode='S01', nama='Cedera Kepala Terbuka', kategori='S'),
            ICD10(kode='S06', nama='Cedera Kepala Intra Kranial', kategori='S'),
            ICD10(kode='S52', nama='Fraktur Ossa Antebrachii', kategori='S'),
            ICD10(kode='S72', nama='Fraktur Femur', kategori='S'),
            ICD10(kode='S82', nama='Fraktur Tungkai Bawah', kategori='S'),
            ICD10(kode='S83', nama='Dislokasi, Keseleo dan Tegang', kategori='S'),
            ICD10(kode='S90', nama='Cedera Superfisial Abdomen', kategori='S'),

            # U - Kode Khusus
            ICD10(kode='U70', nama='Infeksi Bakteri Resistensi', kategori='U'),
            ICD10(kode='U71', nama='Infeksi Virus Lain', kategori='U'),
            ICD10(kode='U88', nama='BPJS - Gigi', kategori='U'),
        ]

        for icd in icd10_list:
            db.session.add(icd)

        db.session.commit()

        # Create Sample ICD-9 Codes (Tindakan Medis)
        icd9_list = [
            # Tindakan Umum
            ICD9(kode='00.01', nama='Transfusi darah', kategori='tindakan'),
            ICD9(kode='00.02', nama='Pemberian obat intravena', kategori='tindakan'),
            ICD9(kode='00.09', nama='Pemberian terapi IV lain', kategori='tindakan'),

            # Tindakan Diagnostik
            ICD9(kode='87.03', nama='Rontgen Thorax', kategori='diagnostik'),
            ICD9(kode='87.36', nama='IVP (Intravenous Pyelogram)', kategori='diagnostik'),
            ICD9(kode='87.41', nama='Mammografi', kategori='diagnostik'),
            ICD9(kode='88.01', nama='CT Scan Kepala', kategori='diagnostik'),
            ICD9(kode='88.38', nama='CT Scan Whole Body', kategori='diagnostik'),
            ICD9(kode='88.76', nama='USG Abdomen', kategori='diagnostik'),
            ICD9(kode='88.78', nama='USG Obstetri', kategori='diagnostik'),

            # Tindakan Bedah
            ICD9(kode='06.2', nama='Tiroidektomi partial', kategori='bedah'),
            ICD9(kode='06.3', nama='Tiroidektomi total', kategori='bedah'),
            ICD9(kode='36.1', nama='CABG (Bypass Jantung)', kategori='bedah'),
            ICD9(kode='38.12', nama='Endarterektomi karotid', kategori='bedah'),
            ICD9(kode='38.44', nama='Bypass Aorto-femoral', kategori='bedah'),
            ICD9(kode='45.41', nama='Polipektomi Colon', kategori='bedah'),
            ICD9(kode='45.49', nama='Bedah Colon lain', kategori='bedah'),
            ICD9(kode='51.22', nama='Kolesistektomi Laparoskopi', kategori='bedah'),
            ICD9(kode='51.23', nama='Kolesistektomi Open', kategori='bedah'),
            ICD9(kode='52.51', nama='Pankreatektomi distal', kategori='bedah'),
            ICD9(kode='52.80', nama='Whipple Procedure', kategori='bedah'),
            ICD9(kode='53.00', nama='Herniorapi ventral', kategori='bedah'),
            ICD9(kode='53.11', nama='Herniorapi inguinal', kategori='bedah'),
            ICD9(kode='53.41', nama='Herniorapi femoral', kategori='bedah'),
            ICD9(kode='54.11', nama='Laparotomi Eksplorasi', kategori='bedah'),
            ICD9(kode='54.21', nama='Laparoskopi Diagnostik', kategori='bedah'),
            ICD9(kode='70.4', nama='Histerektomi Abdominal', kategori='bedah'),
            ICD9(kode='70.51', nama='Vaginal Hysterectomy', kategori='bedah'),
            ICD9(kode='71.3', nama='Mastektomi radikal', kategori='bedah'),
            ICD9(kode='71.5', nama='Mastektomi simple', kategori='bedah'),
            ICD9(kode='78.50', nama='Fiksasi internal tulang lain', kategori='bedah'),
            ICD9(kode='79.00', nama='Reduksi tertutup fraktur', kategori='bedah'),
            ICD9(kode='79.10', nama='Reduksi terbuka fraktur', kategori='bedah'),
            ICD9(kode='79.30', nama='Open reduction fracture', kategori='bedah'),
            ICD9(kode='81.00', nama='Artroplasti Total Pinggul', kategori='bedah'),
            ICD9(kode='81.02', nama='Artroplasti Partial Pinggul', kategori='bedah'),
            ICD9(kode='81.40', nama='Artroplasti Total Lutut', kategori='bedah'),
            ICD9(kode='81.80', nama='Rekonstruksi ACL', kategori='bedah'),
            ICD9(kode='82.21', nama='Carpal Tunnel Release', kategori='bedah'),
            ICD9(kode='82.41', nama='Debridement tendon', kategori='bedah'),
            ICD9(kode='83.09', nama='Lainnya insisi fascia', kategori='bedah'),
            ICD9(kode='83.13', nama='Tenotomi', kategori='bedah'),
            ICD9(kode='86.3', nama='Excision skin lesion', kategori='bedah'),
            ICD9(kode='86.4', nama='Debridement luka', kategori='bedah'),
            ICD9(kode='86.60', nama='Skin graft free', kategori='bedah'),
            ICD9(kode='86.69', nama='Skin graft lain', kategori='bedah'),
            ICD9(kode='86.70', nama='Flap kulit', kategori='bedah'),
            ICD9(kode='86.84', nama='Sutur luka besar', kategori='bedah'),
            ICD9(kode='93.11', nama='Fisioterapi', kategori='tindakan'),
            ICD9(kode='93.24', nama='Terapi okupasi', kategori='tindakan'),
            ICD9(kode='93.38', nama='Latihan range of motion', kategori='tindakan'),
            ICD9(kode='93.90', nama='CPAP therapy', kategori='tindakan'),
            ICD9(kode='94.62', nama='Detoksifikasi alkohol', kategori='tindakan'),
            ICD9(kode='96.04', nama='Intubasi endotrakeal', kategori='tindakan'),
            ICD9(kode='96.06', nama='Nasogastric tube', kategori='tindakan'),
            ICD9(kode='96.07', nama='Kateterisasi urin', kategori='tindakan'),
            ICD9(kode='96.71', nama='Ventilasi mekanik', kategori='tindakan'),
            ICD9(kode='97.05', nama='Penggantian kateter', kategori='tindakan'),
            ICD9(kode='97.15', nama='Lavage gastric', kategori='tindakan'),
        ]

        for icd9 in icd9_list:
            db.session.add(icd9)

        db.session.commit()

        # Create Sample INA-CBGs Codes
        inacbgs_list = [
            # Bedah Umum
            INACBGs(kode_cbg='A-1-1', nama_cbg='Appendektomi', tarif=3500000, kategori='bedah', sub_kategori='Abdomen'),
            INACBGs(kode_cbg='A-1-2', nama_cbg='Kolesistektomi Laparoskopi', tarif=5500000, kategori='bedah', sub_kategori='Abdomen'),
            INACBGs(kode_cbg='A-1-3', nama_cbg='Herniorapi Inguinal', tarif=2800000, kategori='bedah', sub_kategori='Hernia'),
            INACBGs(kode_cbg='A-1-4', nama_cbg='Hemoroidectomy', tarif=2200000, kategori='bedah', sub_kategori='Anorektal'),
            INACBGs(kode_cbg='A-1-5', nama_cbg='Tiroidektomi', tarif=4500000, kategori='bedah', sub_kategori='Endokrin'),

            # Bedah Ortopedi
            INACBGs(kode_cbg='B-1-1', nama_cbg='Artroplasti Total Pggul', tarif=25000000, kategori='bedah', sub_kategori='Ortopedi'),
            INACBGs(kode_cbg='B-1-2', nama_cbg='Artroplasti Total Lutut', tarif=22000000, kategori='bedah', sub_kategori='Ortopedi'),
            INACBGs(kode_cbg='B-1-3', nama_cbg='Open Reduction Internal Fixation', tarif=8500000, kategori='bedah', sub_kategori='Ortopedi'),
            INACBGs(kode_cbg='B-1-4', nama_cbg='Spinal Fusion', tarif=18000000, kategori='bedah', sub_kategori='Ortopedi'),
            INACBGs(kode_cbg='B-1-5', nama_cbg='Amputasi', tarif=4500000, kategori='bedah', sub_kategori='Ortopedi'),

            # Bedah Syaraf
            INACBGs(kode_cbg='C-1-1', nama_cbg='Kraniotomi', tarif=15000000, kategori='bedah', sub_kategori='Saraf'),
            INACBGs(kode_cbg='C-1-2', nama_cbg='Cranioplasty', tarif=8500000, kategori='bedah', sub_kategori='Saraf'),
            INACBGs(kode_cbg='C-1-3', nama_cbg='Ventriculostomy', tarif=6500000, kategori='bedah', sub_kategori='Saraf'),
            INACBGs(kode_cbg='C-1-4', nama_cbg='Laminektomi', tarif=9500000, kategori='bedah', sub_kategori='Saraf'),

            # Bedah Jantung
            INACBGs(kode_cbg='D-1-1', nama_cbg='CABG', tarif=35000000, kategori='bedah', sub_kategori='Jantung'),
            INACBGs(kode_cbg='D-1-2', nama_cbg='Valve Replacement', tarif=40000000, kategori='bedah', sub_kategori='Jantung'),
            INACBGs(kode_cbg='D-1-3', nama_cbg='Pacemaker Insertion', tarif=12000000, kategori='bedah', sub_kategori='Jantung'),
            INACBGs(kode_cbg='D-1-4', nama_cbg='Angioplasty', tarif=15000000, kategori='bedah', sub_kategori='Jantung'),

            # Bedah Mulut/Mata/THT
            INACBGs(kode_cbg='E-1-1', nama_cbg='Mastektomi', tarif=6500000, kategori='bedah', sub_kategori='Breast'),
            INACBGs(kode_cbg='E-1-2', nama_cbg='Lumpektomi', tarif=4500000, kategori='bedah', sub_kategori='Breast'),
            INACBGs(kode_cbg='E-1-3', nama_cbg='Thyroidectomy', tarif=5500000, kategori='bedah', sub_kategori='Endokrin'),

            # Non-Bedah Internis
            INACBGs(kode_cbg='F-1-1', nama_cbg='Pneumonia Biasa', tarif=2500000, kategori='non-bedah', sub_kategori='Paru'),
            INACBGs(kode_cbg='F-1-2', nama_cbg='Pneumonia Berat', tarif=4500000, kategori='non-bedah', sub_kategori='Paru'),
            INACBGs(kode_cbg='F-1-3', nama_cbg='Asma Bronkial', tarif=2000000, kategori='non-bedah', sub_kategori='Paru'),
            INACBGs(kode_cbg='F-1-4', nama_cbg='TB Paru', tarif=1800000, kategori='non-bedah', sub_kategori='Paru'),

            # Non-Bedah Jantung
            INACBGs(kode_cbg='G-1-1', nama_cbg='CHF (Gagal Jantung)', tarif=3500000, kategori='non-bedah', sub_kategori='Jantung'),
            INACBGs(kode_cbg='G-1-2', nama_cbg='Hipertensi Berat', tarif=2200000, kategori='non-bedah', sub_kategori='Jantung'),
            INACBGs(kode_cbg='G-1-3', nama_cbg='Aritmia', tarif=2800000, kategori='non-bedah', sub_kategori='Jantung'),
            INACBGs(kode_cbg='G-1-4', nama_cbg='Infark Miokard', tarif=4500000, kategori='non-bedah', sub_kategori='Jantung'),

            # Non-Bedah Neurologi
            INACBGs(kode_cbg='H-1-1', nama_cbg='Stroke Iskemik', tarif=4500000, kategori='non-bedah', sub_kategori='Saraf'),
            INACBGs(kode_cbg='H-1-2', nama_cbg='Stroke Hemoragik', tarif=5500000, kategori='non-bedah', sub_kategori='Saraf'),
            INACBGs(kode_cbg='H-1-3', nama_cbg='Meningitis', tarif=3500000, kategori='non-bedah', sub_kategori='Saraf'),
            INACBGs(kode_cbg='H-1-4', nama_cbg='Epilepsi', tarif=2000000, kategori='non-bedah', sub_kategori='Saraf'),

            # Non-Bedah GIT
            INACBGs(kode_cbg='I-1-1', nama_cbg='Diare Dehidrasi', tarif=1500000, kategori='non-bedah', sub_kategori='GIT'),
            INACBGs(kode_cbg='I-1-2', nama_cbg='Perdarahan GIT', tarif=3500000, kategori='non-bedah', sub_kategori='GIT'),
            INACBGs(kode_cbg='I-1-3', nama_cbg='Sirosis Hati', tarif=2800000, kategori='non-bedah', sub_kategori='GIT'),
            INACBGs(kode_cbg='I-1-4', nama_cbg='Pankreatitis Akut', tarif=4000000, kategori='non-bedah', sub_kategori='GIT'),

            # Non-Bedah Ginjal
            INACBGs(kode_cbg='J-1-1', nama_cbg='Gagal Ginjal Kronik', tarif=3500000, kategori='non-bedah', sub_kategori='Ginjal'),
            INACBGs(kode_cbg='J-1-2', nama_cbg='ISK (Infeksi Saluran Kemih)', tarif=1800000, kategori='non-bedah', sub_kategori='Ginjal'),
            INACBGs(kode_cbg='J-1-3', nama_cbg='Nefrolitiasis', tarif=2200000, kategori='non-bedah', sub_kategori='Ginjal'),

            # Kandungan
            INACBGs(kode_cbg='K-1-1', nama_cbg='Persalinan Normal', tarif=1500000, kategori='ibu', sub_kategori='Persalinan'),
            INACBGs(kode_cbg='K-1-2', nama_cbg='SC (Sectio Caesarea)', tarif=3500000, kategori='ibu', sub_kategori='Persalinan'),
            INACBGs(kode_cbg='K-1-3', nama_cbg='Abortus Incomplete', tarif=1200000, kategori='ibu', sub_kategori='Abortus'),
            INACBGs(kode_cbg='K-1-4', nama_cbg='Kuretase', tarif=1000000, kategori='ibu', sub_kategori='Kandungan'),

            # Neonatus
            INACBGs(kode_cbg='L-1-1', nama_cbg='BBLR (Bawah 2500g)', tarif=3500000, kategori='neonatus', sub_kategori='Perawatan'),
            INACBGs(kode_cbg='L-1-2', nama_cbg='Asfiksia Neonatorum', tarif=2800000, kategori='neonatus', sub_kategori='Perawatan'),
            INACBGs(kode_cbg='L-1-3', nama_cbg='Jaundice Neonatorum', tarif=1800000, kategori='neonatus', sub_kategori='Perawatan'),

            # Anak
            INACBGs(kode_cbg='M-1-1', nama_cbg='Pneumonia Anak', tarif=2000000, kategori='non-bedah', sub_kategori='Anak'),
            INACBGs(kode_cbg='M-1-2', nama_cbg='Demam Berdarah Dengue', tarif=2800000, kategori='non-bedah', sub_kategori='Anak'),
            INACBGs(kode_cbg='M-1-3', nama_cbg='Diare Anak Dehidrasi', tarif=1500000, kategori='non-bedah', sub_kategori='Anak'),
            INACBGs(kode_cbg='M-1-4', nama_cbg='Meningitis Anak', tarif=3500000, kategori='non-bedah', sub_kategori='Anak'),
        ]

        for inac in inacbgs_list:
            db.session.add(inac)

        db.session.commit()

        print('Database berhasil diinisialisasi!')
        print('=' * 50)
        print('Admin User:')
        print('  Username: admin')
        print('  Password: admin123')
        print('=' * 50)
        print('\nData Awal:')
        print(f'  - {len(poliklinik_list)} Poliklinik')
        print(f'  - {len(kamar_list)} Kamar')
        print(f'  - {sum(len(n) for n in tt_data)} Tempat Tidur')
        print(f'  - {len(obat_list)} Obat')
        print(f'  - {len(icd10_list)} Kode ICD-10')
        print(f'  - {len(icd9_list)} Kode ICD-9')
        print(f'  - {len(inacbgs_list)} Kode INA-CBGs')

if __name__ == '__main__':
    init_db()
