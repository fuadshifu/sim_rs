from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Pasien, SEP, ICD10, Rujukan, Klaim, KlaimDetail
from app.services.bpjs_service import bpjs_service
from datetime import datetime, date
import random
import string

bpjs_bp = Blueprint('bpjs', __name__, url_prefix='/bpjs')

def generate_nomor_sep():
    """Generate nomor SEP secara unik"""
    today = datetime.now().strftime('%Y%m%d')
    random_suffix = ''.join(random.choices(string.digits, k=6))
    return f"030{today}{random_suffix}"

@bpjs_bp.route('/sep')
@login_required
def sep_list():
    """Daftar SEP yang pernah dibuat"""
    sep_list = SEP.query.order_by(SEP.tanggal_sep.desc()).limit(50).all()
    return render_template('bpjs/sep_list.html', sep_list=sep_list)

@bpjs_bp.route('/sep/baru', methods=['GET', 'POST'])
@login_required
def sep_baru():
    """Buat SEP baru untuk pasien"""
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        faskes_asal = request.form.get('faskes_asal')
        diagnosa_awal = request.form.get('diagnosa_awal')
        icd10_id = request.form.get('icd10_id')
        kelas_rawat = request.form.get('kelas_rawat')
        referensi = request.form.get('referensi')

        pasien = Pasien.query.get_or_404(pasien_id)

        # Validasi pasien punya BPJS
        if not pasien.no_bpjs:
            flash('Pasien tidak memiliki nomor BPJS!', 'danger')
            return redirect(url_for('bpjs.sep_baru'))

        if not pasien.no_bpjs or pasien.status_bpjs != 'aktif':
            flash('BPJS pasien tidak aktif!', 'danger')
            return redirect(url_for('bpjs.sep_baru'))

        # Generate nomor SEP
        nomor_sep = generate_nomor_sep()

        sep = SEP(
            pasien_id=pasien_id,
            nomor_sep=nomor_sep,
            tanggal_sep=datetime.now(),
            faskes_asal=faskes_asal,
            diagnosa_awal=diagnosa_awal,
            icd10_awal_id=icd10_id,
            kelas_rawat=kelas_rawat or pasien.kelas_bpjs,
            status='aktif',
            referensi=referensi
        )

        db.session.add(sep)
        db.session.commit()

        flash(f'SEP berhasil dibuat: {nomor_sep}', 'success')
        return redirect(url_for('bpjs.sep_detail', id=sep.id))

    # GET - show form
    search = request.args.get('search', '')
    if search:
        pasien_list = Pasien.query.filter(
            Pasien.aktif == True,
            (Pasien.nama_lengkap.like(f'%{search}%')) |
            (Pasien.nik.like(f'%{search}%')) |
            (Pasien.no_bpjs.like(f'%{search}%'))
        ).filter(Pasien.no_bpjs.isnot(None)).all()
    else:
        pasien_list = []

    # Get ICD-10 for dropdown
    icd10_list = ICD10.query.filter_by(aktif=True).order_by(ICD10.kode).limit(50).all()

    return render_template('bpjs/sep_baru.html',
                         pasien_list=pasien_list,
                         icd10_list=icd10_list,
                         search=search)

@bpjs_bp.route('/sep/<int:id>')
@login_required
def sep_detail(id):
    """Detail SEP"""
    sep = SEP.query.get_or_404(id)
    return render_template('bpjs/sep_detail.html', sep=sep)

@bpjs_bp.route('/sep/cari-pasien')
@login_required
def cari_pasien():
    """Cari pasien untuk AJAX"""
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify([])

    pasien_list = Pasien.query.filter(
        Pasien.aktif == True,
        Pasien.no_bpjs.isnot(None),
        (Pasien.nama_lengkap.like(f'%{q}%')) |
        (Pasien.nik.like(f'%{q}%')) |
        (Pasien.no_bpjs.like(f'%{q}%'))
    ).limit(10).all()

    return jsonify([{
        'id': p.id,
        'nama': p.nama_lengkap,
        'nik': p.nik,
        'bpjs': p.no_bpjs,
        'kelas': p.kelas_bpjs,
        'status': p.status_bpjs
    } for p in pasien_list])

# ==================== RUJUKAN ====================

def generate_nomor_rujukan():
    """Generate nomor rujukan secara unik"""
    today = datetime.now().strftime('%Y%m%d')
    random_suffix = ''.join(random.choices(string.digits, k=6))
    return f"RUJ{today}{random_suffix}"

@bpjs_bp.route('/rujukan')
@login_required
def rujukan_list():
    """Daftar rujukan"""
    status_filter = request.args.get('status', '')
    jenis_filter = request.args.get('jenis', '')

    query = Rujukan.query

    if status_filter:
        query = query.filter_by(status=status_filter)
    if jenis_filter:
        query = query.filter_by(jenis_rujukan=jenis_filter)

    rujukan_list = query.order_by(Rujukan.tanggal_rujukan.desc()).all()
    return render_template('bpjs/rujukan_list.html', rujukan_list=rujukan_list)

@bpjs_bp.route('/rujukan/baru', methods=['GET', 'POST'])
@login_required
def rujukan_baru():
    """Buat rujukan baru"""
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        sep_id = request.form.get('sep_id')
        faskes_tujuan = request.form.get('faskes_tujuan')
        faskes_asal = request.form.get('faskes_asal')
        diagnosa = request.form.get('diagnosa')
        icd10_id = request.form.get('icd10_id')
        catatan = request.form.get('catatan')
        jenis_rujukan = request.form.get('jenis_rujukan', 'keluar')

        pasien = Pasien.query.get_or_404(pasien_id)

        # Generate nomor rujukan
        nomor_rujukan = generate_nomor_rujukan()

        rujukan = Rujukan(
            pasien_id=pasien_id,
            sep_id=sep_id,
            nomor_rujukan=nomor_rujukan,
            tanggal_rujukan=datetime.now(),
            faskes_tujuan=faskes_tujuan,
            faskes_asal=faskes_asal,
            diagnosa=diagnosa,
            icd10_id=icd10_id,
            catatan=catatan,
            jenis_rujukan=jenis_rujukan,
            status='aktif'
        )

        db.session.add(rujukan)
        db.session.commit()

        flash(f'Rujukan berhasil dibuat: {nomor_rujukan}', 'success')
        return redirect(url_for('bpjs.rujukan_detail', id=rujukan.id))

    # GET - show form
    search = request.args.get('search', '')
    if search:
        pasien_list = Pasien.query.filter(
            Pasien.aktif == True,
            (Pasien.nama_lengkap.like(f'%{search}%')) |
            (Pasien.nik.like(f'%{search}%'))
        ).all()
    else:
        pasien_list = []

    # Get SEP aktif for dropdown
    sep_list = SEP.query.filter_by(status='aktif').all()
    icd10_list = ICD10.query.filter_by(aktif=True).order_by(ICD10.kode).limit(50).all()

    return render_template('bpjs/rujukan_baru.html',
                         pasien_list=pasien_list,
                         sep_list=sep_list,
                         icd10_list=icd10_list,
                         search=search)

@bpjs_bp.route('/rujukan/<int:id>')
@login_required
def rujukan_detail(id):
    """Detail rujukan"""
    rujukan = Rujukan.query.get_or_404(id)
    return render_template('bpjs/rujukan_detail.html', rujukan=rujukan)

@bpjs_bp.route('/rujukan/<int:id>/update-status', methods=['POST'])
@login_required
def rujukan_update_status(id):
    """Update status rujukan"""
    rujukan = Rujukan.query.get_or_404(id)
    new_status = request.form.get('status')

    rujukan.status = new_status
    db.session.commit()

    flash(f'Status rujukan diperbarui menjadi: {new_status}', 'success')
    return redirect(url_for('bpjs.rujukan_detail', id=id))

# ==================== KLAIM ====================

def generate_nomor_klaim():
    """Generate nomor klaim secara unik"""
    today = datetime.now().strftime('%Y%m%d')
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"KLM{today}{random_suffix}"

@bpjs_bp.route('/klaim')
@login_required
def klaim_list():
    """Daftar klaim"""
    status_filter = request.args.get('status', '')

    query = Klaim.query
    if status_filter:
        query = query.filter_by(status_klaim=status_filter)

    klaim_list = query.order_by(Klaim.created_at.desc()).all()
    return render_template('bpjs/klaim_list.html', klaim_list=klaim_list)

@bpjs_bp.route('/klaim/baru', methods=['GET', 'POST'])
@login_required
def klaim_baru():
    """Buat klaim baru"""
    if request.method == 'POST':
        periode_awal = request.form.get('periode_awal')
        periode_akhir = request.form.get('periode_akhir')
        catatan = request.form.get('catatan')

        # Generate nomor klaim
        nomor_klaim = generate_nomor_klaim()

        klaim = Klaim(
            nomor_klaim=nomor_klaim,
            periode_awal=datetime.strptime(periode_awal, '%Y-%m-%d').date() if periode_awal else None,
            periode_akhir=datetime.strptime(periode_akhir, '%Y-%m-%d').date() if periode_akhir else None,
            status_klaim='draft',
            catatan=catatan
        )

        db.session.add(klaim)
        db.session.commit()

        flash(f'Klaim berhasil dibuat: {nomor_klaim}', 'success')
        return redirect(url_for('bpjs.klaim_detail', id=klaim.id))

    return render_template('bpjs/klaim_baru.html')

@bpjs_bp.route('/claim/<int:id>')
@login_required
def klaim_detail(id):
    """Detail klaim"""
    klaim = Klaim.query.get_or_404(id)
    sep_list = SEP.query.filter(
        SEP.status == 'aktif',
        SEP.tanggal_sep >= klaim.periode_awal if klaim.periode_awal else True,
        SEP.tanggal_sep <= klaim.periode_akhir if klaim.periode_akhir else True
    ).all() if klaim.periode_awal else SEP.query.filter_by(status='aktif').all()
    return render_template('bpjs/klaim_detail.html', klaim=klaim, sep_list=sep_list)

@bpjs_bp.route('/klaim/<int:id>/tambah-sep', methods=['POST'])
@login_required
def klaim_tambah_sep(id):
    """Tambah SEP ke klaim"""
    klaim = Klaim.query.get_or_404(id)
    sep_id = request.form.get('sep_id')
    diagnose = request.form.get('diagnose')
    icd10_id = request.form.get('icd10_id')
    prosedur = request.form.get('prosedur')
    tarif = request.form.get('tarif', 0)

    sep = SEP.query.get_or_404(sep_id)

    detail = KlaimDetail(
        klaim_id=id,
        sep_id=sep_id,
        diagnose=diagnose,
        icd10_id=icd10_id,
        prosedur=prosedur,
        tarif=tarif
    )

    db.session.add(detail)

    # Update total tarif klaim
    klaim.total_tarif = float(klaim.total_tarif or 0) + float(tarif or 0)
    db.session.commit()

    flash('SEP ditambahkan ke klaim', 'success')
    return redirect(url_for('bpjs.klaim_detail', id=id))

@bpjs_bp.route('/klaim/<int:id>/submit', methods=['POST'])
@login_required
def klaim_submit(id):
    """Submit klaim ke BPJS"""
    klaim = Klaim.query.get_or_404(id)

    # Update status
    klaim.status_klaim = 'submitted'
    klaim.tanggal_submit = datetime.now()
    db.session.commit()

    flash('Klaim berhasil disubmit ke BPJS', 'success')
    return redirect(url_for('bpjs.klaim_detail', id=id))

@bpjs_bp.route('/claim/<int:id>/bayar', methods=['POST'])
@login_required
def klaim_bayar(id):
    """Tandai klaim lunas"""
    klaim = Klaim.query.get_or_404(id)

    klaim.status_klaim = 'paid'
    klaim.tanggal_bayar = datetime.now()
    db.session.commit()

    flash('Klaim ditandai lunas', 'success')
    return redirect(url_for('bpjs.klaim_detail', id=id))

# ==================== UPDATE SEP ====================

@bpjs_bp.route('/sep/<int:id>/update', methods=['GET', 'POST'])
@login_required
def sep_update(id):
    """Update data SEP"""
    sep = SEP.query.get_or_404(id)

    if request.method == 'POST':
        sep.faskes_asal = request.form.get('faskes_asal')
        sep.diagnosa_awal = request.form.get('diagnosa_awal')
        sep.icd10_awal_id = request.form.get('icd10_id')
        sep.kelas_rawat = request.form.get('kelas_rawat')
        sep.referensi = request.form.get('referensi')

        db.session.commit()
        flash('SEP berhasil diperbarui', 'success')
        return redirect(url_for('bpjs.sep_detail', id=sep.id))

    icd10_list = ICD10.query.filter_by(aktif=True).order_by(ICD10.kode).all()
    return render_template('bpjs/sep_update.html', sep=sep, icd10_list=icd10_list)

@bpjs_bp.route('/sep/<int:id>/lanjutkan', methods=['POST'])
@login_required
def sep_lanjutkan(id):
    """Lanjutkan SEP ke periode baru"""
    sep = SEP.query.get_or_404(id)

    # Buat SEP baru dengan nomor berbeda
    nomor_sep_baru = generate_nomor_sep()

    sep_baru = SEP(
        pasien_id=sep.pasien_id,
        nomor_sep=nomor_sep_baru,
        tanggal_sep=datetime.now(),
        faskes_asal=sep.faskes_asal,
        diagnosa_awal=sep.diagnosa_awal,
        icd10_awal_id=sep.icd10_awal_id,
        kelas_rawat=sep.kelas_rawat,
        status='aktif',
        referensi=sep.referensi
    )

    # Tandai SEP lama expired
    sep.status = 'expired'

    db.session.add(sep_baru)
    db.session.commit()

    flash(f'SEP berhasil dilanjutkan: {nomor_sep_baru}', 'success')
    return redirect(url_for('bpjs.sep_detail', id=sep_baru.id))

# ==================== API MOCK ====================

@bpjs_bp.route('/api/eligibilitas', methods=['POST'])
@login_required
def api_eligibilitas():
    """API mock cek eligibilitas BPJS"""
    data = request.get_json()
    no_kartu = data.get('no_kartu', '')
    tgl_layanan = data.get('tgl_layanan')

    if tgl_layanan:
        tgl = datetime.strptime(tgl_layanan, '%Y-%m-%d').date()
    else:
        tgl = date.today()

    # Panggil service
    result = bpjs_service.cek_eligibilitas(no_kartu, tgl)

    return jsonify(result)

@bpjs_bp.route('/api/SEP', methods=['POST'])
@login_required
def api_create_sep():
    """API mock buat SEP"""
    data = request.get_json()

    result = bpjs_service.create_sep(data)

    return jsonify(result)