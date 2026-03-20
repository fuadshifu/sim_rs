"""
Jadwal Dokter Routes
Manajemen jadwal praktik dokter per poliklinik
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import JadwalDokter, User, Poliklinik
from datetime import datetime, time

jadwal_bp = Blueprint('jadwal', __name__, url_prefix='/jadwal')

@jadwal_bp.route('/dokter')
@login_required
def dokter_list():
    """Daftar jadwal dokter"""
    poliklinik_filter = request.args.get('poliklinik', '')
    hari_filter = request.args.get('hari', '')

    query = JadwalDokter.query.filter_by(aktif=True)

    if poliklinik_filter:
        query = query.filter_by(poliklinik_id=poliklinik_filter)
    if hari_filter:
        query = query.filter_by(hari=hari_filter)

    jadwal_list = query.order_by('hari', 'jam_mulai').all()

    poliklinik_list = Poliklinik.query.filter_by(aktif=True).all()

    return render_template('jadwal/dokter_list.html',
                         jadwal_list=jadwal_list,
                         poliklinik_list=poliklinik_list,
                         poliklinik_filter=poliklinik_filter,
                         hari_filter=hari_filter)

@jadwal_bp.route('/dokter/baru', methods=['GET', 'POST'])
@login_required
def dokter_baru():
    """Tambah jadwal dokter baru"""
    if request.method == 'POST':
        dokter_id = request.form.get('dokter_id')
        poliklinik_id = request.form.get('poliklinik_id')
        hari = request.form.get('hari')
        jam_mulai = request.form.get('jam_mulai')
        jam_selesai = request.form.get('jam_selesai')
        kapasitas = request.form.get('kapasitas', 20)

        # Cek duplikasi
        existing = JadwalDokter.query.filter_by(
            dokter_id=dokter_id,
            poliklinik_id=poliklinik_id,
            hari=hari
        ).first()

        if existing:
            flash('Jadwal sudah ada untuk dokter ini pada hari yang sama!', 'danger')
            return redirect(url_for('jadwal.dokter_baru'))

        jadwal = JadwalDokter(
            dokter_id=dokter_id,
            poliklinik_id=poliklinik_id,
            hari=hari,
            jam_mulai=datetime.strptime(jam_mulai, '%H:%M').time() if jam_mulai else None,
            jam_selesai=datetime.strptime(jam_selesai, '%H:%M').time() if jam_selesai else None,
            kapasitas=kapasitas,
            aktif=True
        )

        db.session.add(jadwal)
        db.session.commit()

        flash('Jadwal dokter berhasil ditambahkan!', 'success')
        return redirect(url_for('jadwal.dokter_list'))

    # Get doctors with role dokter
    from app.models import Role
    dokter_role = Role.query.filter_by(name='dokter').first()
    dokter_list = User.query.filter_by(role_id=dokter_role.id, aktif=True).all() if dokter_role else []

    poliklinik_list = Poliklinik.query.filter_by(aktif=True).all()

    return render_template('jadwal/dokter_baru.html',
                         dokter_list=dokter_list,
                         poliklinik_list=poliklinik_list)

@jadwal_bp.route('/dokter/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def dokter_edit(id):
    """Edit jadwal dokter"""
    jadwal = JadwalDokter.query.get_or_404(id)

    if request.method == 'POST':
        jadwal.poliklinik_id = request.form.get('poliklinik_id')
        jadwal.hari = request.form.get('hari')
        jam_mulai = request.form.get('jam_mulai')
        jam_selesai = request.form.get('jam_selesai')
        jadwal.kapasitas = request.form.get('kapasitas', 20)
        jadwal.aktif = 'aktif' in request.form

        if jam_mulai:
            jadwal.jam_mulai = datetime.strptime(jam_mulai, '%H:%M').time()
        if jam_selesai:
            jadwal.jam_selesai = datetime.strptime(jam_selesai, '%H:%M').time()

        db.session.commit()

        flash('Jadwal dokter berhasil diperbarui!', 'success')
        return redirect(url_for('jadwal.dokter_list'))

    from app.models import Role
    dokter_role = Role.query.filter_by(name='dokter').first()
    dokter_list = User.query.filter_by(role_id=dokter_role.id, aktif=True).all() if dokter_role else []

    poliklinik_list = Poliklinik.query.filter_by(aktif=True).all()

    return render_template('jadwal/dokter_edit.html',
                         jadwal=jadwal,
                         dokter_list=dokter_list,
                         poliklinik_list=poliklinik_list)

@jadwal_bp.route('/dokter/<int:id>/delete', methods=['POST'])
@login_required
def dokter_delete(id):
    """Hapus jadwal dokter"""
    jadwal = JadwalDokter.query.get_or_404(id)
    jadwal.aktif = False
    db.session.commit()

    flash('Jadwal dokter berhasil dihapus!', 'success')
    return redirect(url_for('jadwal.dokter_list'))

@jadwal_bp.route('/dokter/api/<hari>')
@login_required
def dokter_api_hari(hari):
    """Get jadwal dokter berdasarkan hari (JSON API)"""
    jadwal_list = JadwalDokter.query.filter_by(hari=hari, aktif=True).all()

    return jsonify([{
        'id': j.id,
        'dokter_id': j.dokter_id,
        'dokter_nama': j.dokter.nama_lengkap if j.dokter else '',
        'poliklinik_id': j.poliklinik_id,
        'poliklinik_nama': j.poliklinik.nama if j.poliklinik else '',
        'hari': j.hari,
        'jam_mulai': j.jam_mulai.strftime('%H:%M') if j.jam_mulai else '',
        'jam_selesai': j.jam_selesai.strftime('%H:%M') if j.jam_selesai else '',
        'kapasitas': j.kapasitas
    } for j in jadwal_list])

@jadwal_bp.route('/dokter/api/poliklinik/<int:poliklinik_id>')
@login_required
def dokter_api_poliklinik(poliklinik_id):
    """Get jadwal dokter berdasarkan poliklinik (JSON API)"""
    hari = request.args.get('hari', '')

    query = JadwalDokter.query.filter_by(poliklinik_id=poliklinik_id, aktif=True)
    if hari:
        query = query.filter_by(hari=hari)

    jadwal_list = query.all()

    return jsonify([{
        'id': j.id,
        'dokter_id': j.dokter_id,
        'dokter_nama': j.dokter.nama_lengkap if j.dokter else '',
        'hari': j.hari,
        'jam_mulai': j.jam_mulai.strftime('%H:%M') if j.jam_mulai else '',
        'jam_selesai': j.jam_selesai.strftime('%H:%M') if j.jam_selesai else '',
        'kapasitas': j.kapasitas
    } for j in jadwal_list])
