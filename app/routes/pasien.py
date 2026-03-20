from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Pasien
from datetime import datetime

pasien_bp = Blueprint('pasien', __name__, url_prefix='/pasien')

@pasien_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '')
    if search:
        pasien_list = Pasien.query.filter(
            (Pasien.nik.like(f'%{search}%')) |
            (Pasien.nama_lengkap.like(f'%{search}%'))
        ).filter_by(aktif=True).order_by(Pasien.created_at.desc()).all()
    else:
        pasien_list = Pasien.query.filter_by(aktif=True).order_by(Pasien.created_at.desc()).all()

    return render_template('pasien/index.html', pasien_list=pasien_list, search=search)

@pasien_bp.route('/baru', methods=['GET', 'POST'])
@login_required
def baru():
    if request.method == 'POST':
        nik = request.form.get('nik')
        nama_lengkap = request.form.get('nama_lengkap')
        tanggal_lahir = request.form.get('tanggal_lahir')
        jenis_kelamin = request.form.get('jenis_kelamin')
        alamat = request.form.get('alamat')
        no_telepon = request.form.get('no_telepon')
        nama_keluarga = request.form.get('nama_keluarga')
        no_keluarga = request.form.get('no_keluarga')
        goldarah = request.form.get('goldarah')
        alergiobat = request.form.get('alergiobat')

        # BPJS fields
        no_bpjs = request.form.get('no_bpjs')
        kelas_bpjs = request.form.get('kelas_bpjs')
        status_bpjs = request.form.get('status_bpjs')
        faskes_tingkat_1 = request.form.get('faskes_tingkat_1')

        # Validasi NIK unik
        if Pasien.query.filter_by(nik=nik).first():
            flash('NIK sudah terdaftar!', 'danger')
            return render_template('pasien/baru.html')

        try:
            tanggal_lahir_date = datetime.strptime(tanggal_lahir, '%Y-%m-%d').date()
        except ValueError:
            flash('Format tanggal lahir tidak valid!', 'danger')
            return render_template('pasien/baru.html')

        pasien = Pasien(
            nik=nik,
            nama_lengkap=nama_lengkap,
            tanggal_lahir=tanggal_lahir_date,
            jenis_kelamin=jenis_kelamin,
            alamat=alamat,
            no_telepon=no_telepon,
            nama_keluarga=nama_keluarga,
            no_keluarga=no_keluarga,
            goldarah=goldarah,
            alergiobat=alergiobat,
            no_bpjs=no_bpjs,
            kelas_bpjs=kelas_bpjs,
            status_bpjs=status_bpjs,
            faskes_tingkat_1=faskes_tingkat_1,
            aktif=True
        )

        db.session.add(pasien)
        db.session.commit()

        flash(f'Pasien {nama_lengkap} berhasil didaftarkan!', 'success')
        return redirect(url_for('pasien.index'))

    return render_template('pasien/baru.html')

@pasien_bp.route('/<int:id>')
@login_required
def detail(id):
    pasien = Pasien.query.get_or_404(id)
    return render_template('pasien/detail.html', pasien=pasien)

@pasien_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    pasien = Pasien.query.get_or_404(id)

    if request.method == 'POST':
        pasien.nik = request.form.get('nik')
        pasien.nama_lengkap = request.form.get('nama_lengkap')
        tanggal_lahir = request.form.get('tanggal_lahir')
        pasien.jenis_kelamin = request.form.get('jenis_kelamin')
        pasien.alamat = request.form.get('alamat')
        pasien.no_telepon = request.form.get('no_telepon')
        pasien.nama_keluarga = request.form.get('nama_keluarga')
        pasien.no_keluarga = request.form.get('no_keluarga')
        pasien.goldarah = request.form.get('goldarah')
        pasien.alergiobat = request.form.get('alergiobat')
        pasien.no_bpjs = request.form.get('no_bpjs')
        pasien.kelas_bpjs = request.form.get('kelas_bpjs')
        pasien.status_bpjs = request.form.get('status_bpjs')
        pasien.faskes_tingkat_1 = request.form.get('faskes_tingkat_1')

        try:
            pasien.tanggal_lahir = datetime.strptime(tanggal_lahir, '%Y-%m-%d').date()
        except ValueError:
            flash('Format tanggal lahir tidak valid!', 'danger')
            return render_template('pasien/edit.html', pasien=pasien)

        db.session.commit()
        flash('Data pasien berhasil diperbarui!', 'success')
        return redirect(url_for('pasien.detail', id=pasien.id))

    return render_template('pasien/edit.html', pasien=pasien)

@pasien_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    pasien = Pasien.query.get_or_404(id)
    pasien.aktif = False
    db.session.commit()
    flash('Pasien berhasil dihapus (nonaktif).', 'success')
    return redirect(url_for('pasien.index'))
