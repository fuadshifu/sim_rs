from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import RawatJalan, Pasien, Poliklinik, User
from datetime import datetime

rawat_jalan_bp = Blueprint('rawat_jalan', __name__, url_prefix='/rawat-jalan')

@rawat_jalan_bp.route('/')
@login_required
def index():
    # Get filter parameters
    status = request.args.get('status', '')
    poliklinik_id = request.args.get('poliklinik_id', '')

    query = RawatJalan.query

    if status:
        query = query.filter_by(status=status)
    if poliklinik_id:
        query = query.filter_by(poliklinik_id=poliklinik_id)

    rawat_jalan_list = query.order_by(RawatJalan.tanggal.desc()).all()
    poliklinik_list = Poliklinik.query.filter_by(aktif=True).all()

    return render_template('rawat_jalan/index.html',
                         rawat_jalan_list=rawat_jalan_list,
                         poliklinik_list=poliklinik_list,
                         status=status,
                         poliklinik_id=poliklinik_id)

@rawat_jalan_bp.route('/baru', methods=['GET', 'POST'])
@login_required
def baru():
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        poliklinik_id = request.form.get('poliklinik_id')
        keluhan = request.form.get('keluhan')

        # Get next queue number for this poliklinik today
        today = datetime.now().date()
        last_antrian = RawatJalan.query.filter(
            RawatJalan.poliklinik_id == poliklinik_id,
            db.func.date(RawatJalan.tanggal) == today
        ).order_by(RawatJalan.nomor_antrian.desc()).first()

        nomor_antrian = (last_antrian.nomor_antrian + 1) if last_antrian else 1

        rawat_jalan = RawatJalan(
            pasien_id=pasien_id,
            poliklinik_id=poliklinik_id,
            keluhan=keluhan,
            nomor_antrian=nomor_antrian,
            status='menunggu',
            tanggal=datetime.now()
        )

        db.session.add(rawat_jalan)
        db.session.commit()

        flash(f'Pasien berhasil didaftarkan ke antrian. Nomor: {nomor_antrian}', 'success')
        return redirect(url_for('rawat_jalan.index'))

    pasien_list = Pasien.query.filter_by(aktif=True).all()
    poliklinik_list = Poliklinik.query.filter_by(aktif=True).all()
    return render_template('rawat_jalan/baru.html',
                         pasien_list=pasien_list,
                         poliklinik_list=poliklinik_list)

@rawat_jalan_bp.route('/<int:id>')
@login_required
def detail(id):
    rawat_jalan = RawatJalan.query.get_or_404(id)
    return render_template('rawat_jalan/detail.html', rawat_jalan=rawat_jalan)

@rawat_jalan_bp.route('/<int:id>/periksa', methods=['GET', 'POST'])
@login_required
def periksa(id):
    rawat_jalan = RawatJalan.query.get_or_404(id)

    if request.method == 'POST':
        rawat_jalan.diagnose = request.form.get('diagnose')
        rawat_jalan.terapi = request.form.get('terapi')
        rawat_jalan.dokter_id = current_user.id
        rawat_jalan.status = 'selesai'

        db.session.commit()
        flash('Pemeriksaan selesai!', 'success')
        return redirect(url_for('rawat_jalan.index'))

    return render_template('rawat_jalan/periksa.html', rawat_jalan=rawat_jalan)

@rawat_jalan_bp.route('/<int:id>/panggil')
@login_required
def panggil(id):
    rawat_jalan = RawatJalan.query.get_or_404(id)
    rawat_jalan.status = 'diperiksa'
    db.session.commit()
    flash(f'Memanggil nomor antrian {rawat_jalan.nomor_antrian}', 'info')
    return redirect(url_for('rawat_jalan.index'))

@rawat_jalan_bp.route('/cari-pasien')
@login_required
def cari_pasien():
    search = request.args.get('q', '')
    pasien = Pasien.query.filter(
        (Pasien.nik.like(f'%{search}%')) |
        (Pasien.nama_lengkap.like(f'%{search}%'))
    ).filter_by(aktif=True).limit(10).all()

    return {'results': [{'id': p.id, 'nik': p.nik, 'nama': p.nama_lengkap} for p in pasien]}
