from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import PemeriksaanLab, PemeriksaanLabDetail, JenisPemeriksaan, Pasien
from datetime import datetime
import random
import string

laboratorium_bp = Blueprint('laboratorium', __name__, url_prefix='/laboratorium')

def generate_no_order():
    """Generate unique order number"""
    return f'LAB-{datetime.now().strftime("%Y%m%d")}-{random.randint(1000, 9999)}'

# ========== JENIS PEMERIKSAAN ==========
@laboratorium_bp.route('/jenis')
@login_required
def jenis():
    search = request.args.get('search', '')
    kategori = request.args.get('kategori', '')

    query = JenisPemeriksaan.query.filter_by(aktif=True)

    if search:
        query = query.filter(
            (JenisPemeriksaan.nama.like(f'%{search}%')) |
            (JenisPemeriksaan.kode.like(f'%{search}%'))
        )
    if kategori:
        query = query.filter_by(kategori=kategori)

    jenis_list = query.order_by(JenisPemeriksaan.nama).all()
    return render_template('laboratorium/jenis.html', jenis_list=jenis_list, search=search, kategori=kategori)

@laboratorium_bp.route('/jenis/baru', methods=['GET', 'POST'])
@login_required
def jenis_baru():
    if request.method == 'POST':
        jp = JenisPemeriksaan(
            nama=request.form.get('nama'),
            kode=request.form.get('kode'),
            kategori=request.form.get('kategori'),
            harga=request.form.get('harga') or 0
        )
        db.session.add(jp)
        db.session.commit()
        flash('Jenis pemeriksaan berhasil ditambahkan!', 'success')
        return redirect(url_for('laboratorium.jenis'))

    return render_template('laboratorium/jenis_baru.html')

@laboratorium_bp.route('/jenis/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def jenis_edit(id):
    jp = JenisPemeriksaan.query.get_or_404(id)

    if request.method == 'POST':
        jp.nama = request.form.get('nama')
        jp.kode = request.form.get('kode')
        jp.kategori = request.form.get('kategori')
        jp.harga = request.form.get('harga')
        db.session.commit()
        flash('Jenis pemeriksaan berhasil diperbarui!', 'success')
        return redirect(url_for('laboratorium.jenis'))

    return render_template('laboratorium/jenis_edit.html', jp=jp)

# ========== PEMERIKSAAN LAB ==========
@laboratorium_bp.route('/')
@login_required
def index():
    status = request.args.get('status', '')
    query = PemeriksaanLab.query

    if status:
        query = query.filter_by(status=status)
    else:
        query = query.filter(PemeriksaanLab.status.in_(['menunggu', 'diambil', 'proses']))

    pemeriksaan_list = query.order_by(PemeriksaanLab.tanggal_order.desc()).all()

    return render_template('laboratorium/index.html',
                         pemeriksaan_list=pemeriksaan_list,
                         status=status)

@laboratorium_bp.route('/baru', methods=['GET', 'POST'])
@login_required
def baru():
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        jenis_ids = request.form.getlist('jenis_pemeriksaan_id[]')
        diagnosa = request.form.get('diagnosa')
        catatan = request.form.get('catatan')

        # Create pemeriksaan
        pemeriksaan = PemeriksaanLab(
            pasien_id=pasien_id,
            nomor_order=generate_no_order(),
            dokter_id=current_user.id,
            diagnosa=diagnosa,
            catatan=catatan,
            status='menunggu'
        )
        db.session.add(pemeriksaan)
        db.session.flush()

        # Create details
        for jp_id in jenis_ids:
            if jp_id:
                detail = PemeriksaanLabDetail(
                    pemeriksaan_id=pemeriksaan.id,
                    jenis_pemeriksaan_id=jp_id,
                    status='menunggu'
                )
                db.session.add(detail)

        db.session.commit()
        flash('Order pemeriksaan lab berhasil dibuat!', 'success')
        return redirect(url_for('laboratorium.index'))

    pasien_list = Pasien.query.filter_by(aktif=True).all()
    jenis_list = JenisPemeriksaan.query.filter_by(aktif=True).all()

    return render_template('laboratorium/baru.html',
                         pasien_list=pasien_list,
                         jenis_list=jenis_list)

@laboratorium_bp.route('/<int:id>')
@login_required
def detail(id):
    pemeriksaan = PemeriksaanLab.query.get_or_404(id)
    return render_template('laboratorium/detail.html', pemeriksaan=pemeriksaan)

@laboratorium_bp.route('/<int:id>/ambil-sampel')
@login_required
def ambil_sampel(id):
    pemeriksaan = PemeriksaanLab.query.get_or_404(id)
    pemeriksaan.status = 'diambil'
    db.session.commit()
    flash('Sampel berhasil diambil!', 'success')
    return redirect(url_for('laboratorium.detail', id=pemeriksaan.id))

@laboratorium_bp.route('/<int:id>/proses')
@login_required
def proses(id):
    pemeriksaan = PemeriksaanLab.query.get_or_404(id)
    pemeriksaan.status = 'proses'
    db.session.commit()
    flash('Pemeriksaan sedang diproses!', 'success')
    return redirect(url_for('laboratorium.detail', id=pemeriksaan.id))

@laboratorium_bp.route('/<int:id>/hasil', methods=['GET', 'POST'])
@login_required
def hasil(id):
    pemeriksaan = PemeriksaanLab.query.get_or_404(id)

    if request.method == 'POST':
        for detail in pemeriksaan.details:
            hasil_key = f'hasil_{detail.id}'
            if hasil_key in request.form:
                detail.hasil = request.form.get(hasil_key)
                detail.nilai_normal = request.form.get(f'nilai_normal_{detail.id}')
                detail.unit = request.form.get(f'unit_{detail.id}')
                detail.status = 'selesai'
                detail.tanggal_selesai = datetime.now()

        pemeriksaan.status = 'selesai'
        db.session.commit()
        flash('Hasil pemeriksaan berhasil disimpan!', 'success')
        return redirect(url_for('laboratorium.detail', id=pemeriksaan.id))

    return render_template('laboratorium/hasil.html', pemeriksaan=pemeriksaan)
