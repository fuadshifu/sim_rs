from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import JenisPemeriksaanRadiologi, PemeriksaanRadiologi, PemeriksaanRadiologiDetail, Pasien, User
from datetime import datetime
import os

radiologi_bp = Blueprint('radiologi', __name__, url_prefix='/radiologi')


@radiologi_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')

    query = PemeriksaanRadiologi.query

    if search:
        query = query.join(Pasien).filter(
            db.or_(
                Pasien.nama_lengkap.ilike(f'%{search}%'),
                PemeriksaanRadiologi.no_order.ilike(f'%{search}%')
            )
        )

    if status_filter:
        query = query.filter(PemeriksaanRadiologi.status == status_filter)

    pemeriksaan_list = query.order_by(PemeriksaanRadiologi.tanggal_order.desc()).all()
    return render_template('radiologi/index.html', pemeriksaan_list=pemeriksaan_list, status_filter=status_filter)


@radiologi_bp.route('/baru', methods=['GET', 'POST'])
@login_required
def baru():
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        dokter_pengirim_id = request.form.get('dokter_pengirim_id')
        catatan = request.form.get('catatan')

        # Generate no_order
        last_order = PemeriksaanRadiologi.query.order_by(PemeriksaanRadiologi.id.desc()).first()
        if last_order and last_order.no_order:
            last_num = int(last_order.no_order.split('-')[-1])
            no_order = f'RAD-{last_num + 1:04d}'
        else:
            no_order = 'RAD-0001'

        pemeriksaan = PemeriksaanRadiologi(
            pasien_id=pasien_id,
            no_order=no_order,
            dokter_pengirim_id=dokter_pengirim_id,
            catatan=catatan
        )
        db.session.add(pemeriksaan)
        db.session.commit()

        flash('Order radiologi berhasil dibuat', 'success')
        return redirect(url_for('radiologi.index'))

    pasien_list = Pasien.query.filter(Pasien.aktif == True).all()
    dokter_list = User.query.filter(User.role == 'dokter').all()
    return render_template('radiologi/baru.html', pasien_list=pasien_list, dokter_list=dokter_list)


@radiologi_bp.route('/<int:id>')
@login_required
def detail(id):
    pemeriksaan = PemeriksaanRadiologi.query.get_or_404(id)
    return render_template('radiologi/detail.html', pemeriksaan=pemeriksaan)


@radiologi_bp.route('/<int:id>/update-status', methods=['POST'])
@login_required
def update_status(id):
    pemeriksaan = PemeriksaanRadiologi.query.get_or_404(id)
    new_status = request.form.get('status')

    pemeriksaan.status = new_status
    db.session.commit()

    flash(f'Status diperbarui menjadi {new_status}', 'success')
    return redirect(url_for('radiologi.detail', id=id))


@radiologi_bp.route('/<int:id>/hasil', methods=['GET', 'POST'])
@login_required
def hasil(id):
    pemeriksaan = PemeriksaanRadiologi.query.get_or_404(id)

    if request.method == 'POST':
        jenis_pemeriksaan_id = request.form.get('jenis_pemeriksaan_id')
        hasil = request.form.get('hasil')

        detail = PemeriksaanRadiologiDetail(
            pemeriksaan_radiologi_id=id,
            jenis_pemeriksaan_id=jenis_pemeriksaan_id,
            hasil=hasil,
            tanggal_selesai=datetime.now(),
            teknisi_id=current_user.id
        )
        db.session.add(detail)

        # Update status jika ada detail baru
        if pemeriksaan.status == 'proses':
            pemeriksaan.status = 'selesai'

        db.session.commit()
        flash('Hasil pemeriksaan disimpan', 'success')
        return redirect(url_for('radiologi.detail', id=id))

    jenis_list = JenisPemeriksaanRadiologi.query.filter(JenisPemeriksaanRadiologi.aktif == True).all()
    return render_template('radiologi/hasil.html', pemeriksaan=pemeriksaan, jenis_list=jenis_list)


@radiologi_bp.route('/jenis')
@login_required
def jenis_list():
    search = request.args.get('search', '')
    if search:
        jenis_list = JenisPemeriksaanRadiologi.query.filter(
            JenisPemeriksaanRadiologi.nama.ilike(f'%{search}%')
        ).all()
    else:
        jenis_list = JenisPemeriksaanRadiologi.query.all()
    return render_template('radiologi/jenis_list.html', jenis_list=jenis_list)


@radiologi_bp.route('/jenis/baru', methods=['GET', 'POST'])
@login_required
def jenis_baru():
    if request.method == 'POST':
        nama = request.form.get('nama')
        kategori = request.form.get('kategori')
        deskripsi = request.form.get('deskripsi')

        jenis = JenisPemeriksaanRadiologi(
            nama=nama,
            kategori=kategori,
            deskripsi=deskripsi
        )
        db.session.add(jenis)
        db.session.commit()

        flash('Jenis pemeriksaan radiologi berhasil ditambahkan', 'success')
        return redirect(url_for('radiologi.jenis_list'))

    return render_template('radiologi/jenis_baru.html')


@radiologi_bp.route('/jenis/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def jenis_edit(id):
    jenis = JenisPemeriksaanRadiologi.query.get_or_404(id)

    if request.method == 'POST':
        jenis.nama = request.form.get('nama')
        jenis.kategori = request.form.get('kategori')
        jenis.deskripsi = request.form.get('deskripsi')
        jenis.aktif = 'aktif' in request.form

        db.session.commit()
        flash('Jenis pemeriksaan radiologi diperbarui', 'success')
        return redirect(url_for('radiologi.jenis_list'))

    return render_template('radiologi/jenis_edit.html', jenis=jenis)


@radiologi_bp.route('/api/available')
@login_required
def api_available():
    """JSON: cek ketersediaan layanan radiologi"""
    # Hitung jumlah pemeriksaan yang masih berlangsung
    ongoing = PemeriksaanRadiologi.query.filter(
        PemeriksaanRadiologi.status.in_(['menunggu', 'diambil', 'proses'])
    ).count()

    return jsonify({
        'available': True,
        'ongoing_count': ongoing,
        'message': 'Layanan radiologi tersedia' if ongoing < 10 else 'Layanan radiologi sibuk'
    })