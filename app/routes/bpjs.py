from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Pasien, SEP, ICD10
from datetime import datetime
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