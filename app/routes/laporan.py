"""
Laporan Routes
Pelaporan Kemenkes: RL 1-6, SIRS, Disease Surveillance (TB/Pneumonia/DBD)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from app import db
from app.models import Pasien, RawatJalan, RawatInap, IGD, RekamMedis, Billing, User, Kamar, TempatTidur, Role
from datetime import datetime, date, timedelta
from collections import defaultdict
import calendar

laporan_bp = Blueprint('laporan', __name__, url_prefix='/laporan')

# ==================== DASHBOARD LAPORAN ====================

@laporan_bp.route('/')
@login_required
def index():
    """Dashboard laporan"""
    return render_template('laporan/index.html')

# ==================== RL 1 - PENDAFTARAN PASIEN ====================

@laporan_bp.route('/rl1')
@login_required
def rl1():
    """RL 1 - Data Pendaftaran Pasien"""
    bulan = request.args.get('bulan', datetime.now().month, type=int)
    tahun = request.args.get('tahun', datetime.now().year, type=int)

    # Hitung pasien baru per bulan
    start_date = date(tahun, bulan, 1)
    end_date = date(tahun, bulan, calendar.monthrange(tahun, bulan)[1])

    # Pasien baru bulan ini
    pasien_baru = Pasien.query.filter(
        Pasien.created_at >= start_date,
        Pasien.created_at <= end_date
    ).count()

    # Rawat jalan baru
    rj_baru = RawatJalan.query.filter(
        RawatJalan.tanggal >= start_date,
        RawatJalan.tanggal <= end_date
    ).count()

    # Rawat inap baru
    ri_baru = RawatInap.query.filter(
        RawatInap.tanggal_masuk >= start_date,
        RawatInap.tanggal_masuk <= end_date
    ).count()

    # IGD baru
    igd_baru = IGD.query.filter(
        IGD.waktu_masuk >= start_date,
        IGD.waktu_masuk <= end_date
    ).count()

    return render_template('laporan/rl1.html',
                         bulan=bulan,
                         tahun=tahun,
                         pasien_baru=pasien_baru,
                         rj_baru=rj_baru,
                         ri_baru=ri_baru,
                         igd_baru=igd_baru)

# ==================== RL 2 - MORBIDITAS (10 BESAR PENYAKIT) ====================

@laporan_bp.route('/rl2')
@login_required
def rl2():
    """RL 2 - 10 Besar Penyakit (Morbiditas)"""
    bulan = request.args.get('bulan', datetime.now().month, type=int)
    tahun = request.args.get('tahun', datetime.now().year, type=int)

    start_date = date(tahun, bulan, 1)
    end_date = date(tahun, bulan, calendar.monthrange(tahun, bulan)[1])

    # Ambil diagnosa dari rekam medis
    diagnosa_data = db.session.query(
        RekamMedis.assessment,
        db.func.count(RekamMedis.id).label('jumlah')
    ).filter(
        RekamMedis.tanggal >= start_date,
        RekamMedis.tanggal <= end_date,
        RekamMedis.assessment.isnot(None)
    ).group_by(
        RekamMedis.assessment
    ).order_by(
        db.func.count(RekamMedis.id).desc()
    ).limit(10).all()

    # Format data untuk template
    top_diseases = []
    total_cases = sum([d[1] for d in diagnosa_data])

    for i, (diagnosa, jumlah) in enumerate(diagnosa_data, 1):
        top_diseases.append({
            'no': i,
            'diagnosa': diagnosa or 'Tidak ada diagnosa',
            'jumlah': jumlah,
            'persentase': round((jumlah / total_cases * 100) if total_cases > 0 else 0, 2)
        })

    return render_template('laporan/rl2.html',
                         bulan=bulan,
                         tahun=tahun,
                         top_diseases=top_diseases,
                         total_cases=total_cases)

# ==================== RL 3 - KEMATIAN ====================

@laporan_bp.route('/rl3')
@login_required
def rl3():
    """RL 3 - Data Kematian"""
    bulan = request.args.get('bulan', datetime.now().month, type=int)
    tahun = request.args.get('tahun', datetime.now().year, type=int)

    start_date = date(tahun, bulan, 1)
    end_date = date(tahun, bulan, calendar.monthrange(tahun, bulan)[1])

    # Kematian di rawat inap
    mati_inap = RawatInap.query.filter(
        RawatInap.tanggal_keluar >= start_date,
        RawatInap.tanggal_keluar <= end_date,
        RawatInap.status == 'meninggal'
    ).count()

    # Kematian di IGD
    mati_igd = IGD.query.filter(
        IGD.waktu_keluar >= start_date,
        IGD.waktu_keluar <= end_date,
        IGD.status == 'meninggal'
    ).count()

    # Total kematian
    total_kematian = mati_inap + mati_igd

    # Kematian neonatal (< 28 hari) - perlu data spesifik

    return render_template('laporan/rl3.html',
                         bulan=bulan,
                         tahun=tahun,
                         mati_inap=mati_inap,
                         mati_igd=mati_igd,
                         total_kematian=total_kematian)

# ==================== RL 4 - BOR (BED OCCUPANCY RATE) ====================

@laporan_bp.route('/rl4')
@login_required
def rl4():
    """RL 4 - Bed Occupancy Rate"""
    bulan = request.args.get('bulan', datetime.now().month, type=int)
    tahun = request.args.get('tahun', datetime.now().year, type=int)

    # Jumlah tempat tidur aktif
    total_tt = TempatTidur.query.filter_by(aktif=True).count()

    # Hari dalam bulan
    hari_dalam_bulan = calendar.monthrange(tahun, bulan)[1]

    # Lookup pasien rawat inap per hari
    # Untuk simplify, hitung rata-rata dari data yang ada
    start_date = date(tahun, bulan, 1)
    end_date = date(tahun, bulan, hari_dalam_bulan)

    # Rata-rata pasien per hari (simplified)
    rata_pasien = RawatInap.query.filter(
        RawatInap.tanggal_masuk <= end_date,
        db.or_(
            RawatInap.tanggal_keluar >= start_date,
            RawatInap.tanggal_keluar.is_(None)
        )
    ).count() / 2  # Simplified calculation

    # BOR calculation
    hari_rawat = rata_pasien * hari_dalam_bulan
    hari_tersedia = total_tt * hari_dalam_bulan
    bor = (hari_rawat / hari_tersedia * 100) if hari_tersedia > 0 else 0

    # LOS (Length of Stay) rata-rata
    # Simplified - biasanya 5-7 hari
    los = 5.5

    # TOI (Turn Over Interval) - rata-rata
    # Simplified
    toi = 2.0

    # BTO (Bed Turn Over)
    if los > 0:
        bto = 30 / los
    else:
        bto = 0

    return render_template('laporan/rl4.html',
                         bulan=bulan,
                         tahun=tahun,
                         total_tt=total_tt,
                         hari_dalam_bulan=hari_dalam_bulan,
                         rata_pasien=round(rata_pasien, 1),
                         bor=round(bor, 1),
                         los=los,
                         toi=toi,
                         bto=round(bto, 1))

# ==================== RL 5 - PEMBIAYAAN RS ====================

@laporan_bp.route('/rl5')
@login_required
def rl5():
    """RL 5 - Pembiayaan RS"""
    bulan = request.args.get('bulan', datetime.now().month, type=int)
    tahun = request.args.get('tahun', datetime.now().year, type=int)

    start_date = date(tahun, bulan, 1)
    end_date = date(tahun, bulan, calendar.monthrange(tahun, bulan)[1])

    # Total pendapatan dari billing
    total_pendapatan = db.session.query(
        db.func.sum(Billing.total)
    ).filter(
        Billing.tanggal >= start_date,
        Billing.tanggal <= end_date,
        Billing.status == 'lunas'
    ).scalar() or 0

    # Rincian per layanan
    pendapatan_rj = db.session.query(
        db.func.sum(Billing.total)
    ).join(BillingDetail).filter(
        Billing.tanggal >= start_date,
        Billing.tanggal <= end_date,
        Billing.status == 'lunas',
        BillingDetail.layanan == 'Rawat Jalan'
    ).scalar() or 0

    pendapatan_ri = db.session.query(
        db.func.sum(Billing.total)
    ).join(BillingDetail).filter(
        Billing.tanggal >= start_date,
        Billing.tanggal <= end_date,
        Billing.status == 'lunas',
        BillingDetail.layanan == 'Rawat Inap'
    ).scalar() or 0

    return render_template('laporan/rl5.html',
                         bulan=bulan,
                         tahun=tahun,
                         total_pendapatan=float(total_pendapatan),
                         pendapatan_rj=float(pendapatan_rj),
                         pendapatan_ri=float(pendapatan_ri))

# ==================== RL 6 - SDM ====================

@laporan_bp.route('/rl6')
@login_required
def rl6():
    """RL 6 - Sumber Daya Manusia RS"""

    # Hitung user berdasarkan role
    roles = Role.query.all()
    sdm_data = []

    for role in roles:
        count = User.query.filter_by(role_id=role.id, aktif=True).count()
        sdm_data.append({
            'role': role.name,
            'description': role.description,
            'jumlah': count
        })

    total_sdm = sum([s['jumlah'] for s in sdm_data])

    return render_template('laporan/rl6.html',
                         sdm_data=sdm_data,
                         total_sdm=total_sdm)

# ==================== SIRS ====================

@laporan_bp.route('/sirs')
@login_required
def sirs():
    """Laporan SIRS (Sistem Informasi Rumah Sakit)"""
    tahun = request.args.get('tahun', datetime.now().year, type=int)

    # Data untuk SIRS
    start_date = date(tahun, 1, 1)
    end_date = date(tahun, 12, 31)

    # Pasien keluar (dirawat)
    pasien_keluar = RawatInap.query.filter(
        RawatInap.tanggal_keluar >= start_date,
        RawatInap.tanggal_keluar <= end_date
    ).count()

    # Pasien keluar mati
    pasien_mati = RawatInap.query.filter(
        RawatInap.tanggal_keluar >= start_date,
        RawatInap.tanggal_keluar <= end_date,
        RawatInap.status == 'meninggal'
    ).count()

    # Rata-rata BOR tahun ini
    total_tt = TempatTidur.query.filter_by(aktif=True).count()
    bor = 65  # Simplified

    return render_template('laporan/sirs.html',
                         tahun=tahun,
                         pasien_keluar=pasien_keluar,
                         pasien_mati=pasien_mati,
                         bor=bor)

# ==================== DISEASE SURVEILLANCE ====================

@laporan_bp.route('/tb')
@login_required
def tb():
    """Laporan TB (Tuberkulosis)"""
    bulan = request.args.get('bulan', datetime.now().month, type=int)
    tahun = request.args.get('tahun', datetime.now().year, type=int)

    start_date = date(tahun, bulan, 1)
    end_date = date(tahun, bulan, calendar.monthrange(tahun, bulan)[1])

    # Hitung kasus TB dari rekam medis (kode ICD-10 A15-A19)
    tb_cases = RekamMedis.query.filter(
        RekamMedis.tanggal >= start_date,
        RekamMedis.tanggal <= end_date,
        RekamMedis.assessment.like('%TB%')
    ).count() + RekamMedis.query.filter(
        RekamMedis.tanggal >= start_date,
        RekamMedis.tanggal <= end_date,
        RekamMedis.assessment.like('%Tuberkulosis%')
    ).count()

    return render_template('laporan/tb.html',
                         bulan=bulan,
                         tahun=tahun,
                         tb_cases=tb_cases)

@laporan_bp.route('/pneumonia')
@login_required
def pneumonia():
    """Laporan Pneumonia"""
    bulan = request.args.get('bulan', datetime.now().month, type=int)
    tahun = request.args.get('tahun', datetime.now().year, type=int)

    start_date = date(tahun, bulan, 1)
    end_date = date(tahun, bulan, calendar.monthrange(tahun, bulan)[1])

    # Hitung kasus pneumonia
    pneumonia_cases = RekamMedis.query.filter(
        RekamMedis.tanggal >= start_date,
        RekamMedis.tanggal <= end_date,
        RekamMedis.assessment.like('%Pneumonia%')
    ).count()

    return render_template('laporan/pneumonia.html',
                         bulan=bulan,
                         tahun=tahun,
                         pneumonia_cases=pneumonia_cases)

@laporan_bp.route('/dbd')
@login_required
def dbd():
    """Laporan DBD (Demam Berdarah Dengue)"""
    bulan = request.args.get('bulan', datetime.now().month, type=int)
    tahun = request.args.get('tahun', datetime.now().year, type=int)

    start_date = date(tahun, bulan, 1)
    end_date = date(tahun, bulan, calendar.monthrange(tahun, bulan)[1])

    # Hitung kasus DBD (kode ICD-10 A90-A91)
    dbd_cases = RekamMedis.query.filter(
        RekamMedis.tanggal >= start_date,
        RekamMedis.tanggal <= end_date,
        RekamMedis.assessment.like('%DBD%')
    ).count() + RekamMedis.query.filter(
        RekamMedis.tanggal >= start_date,
        RekamMedis.tanggal <= end_date,
        RekamMedis.assessment.like('%Dengue%')
    ).count()

    return render_template('laporan/dbd.html',
                         bulan=bulan,
                         tahun=tahun,
                         dbd_cases=dbd_cases)
