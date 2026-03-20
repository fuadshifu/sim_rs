from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Obat, Pasien, User, Resep, ResepDetail
from datetime import datetime

farmasi_bp = Blueprint('farmasi', __name__, url_prefix='/farmasi')

# ========== OBAT ==========
@farmasi_bp.route('/obat')
@login_required
def obat():
    search = request.args.get('search', '')
    jenis = request.args.get('jenis', '')

    query = Obat.query.filter_by(aktif=True)

    if search:
        query = query.filter(
            (Obat.nama.like(f'%{search}%')) |
            (Obat.kode.like(f'%{search}%'))
        )
    if jenis:
        query = query.filter_by(jenis=jenis)

    obat_list = query.order_by(Obat.nama).all()

    return render_template('farmasi/obat.html',
                         obat_list=obat_list,
                         search=search,
                         jenis=jenis)

@farmasi_bp.route('/obat/baru', methods=['GET', 'POST'])
@login_required
def obat_baru():
    if request.method == 'POST':
        nama = request.form.get('nama')
        kode = request.form.get('kode')
        jenis = request.form.get('jenis')
        dosis = request.form.get('dosis')
        satuan = request.form.get('satuan')
        stok = request.form.get('stok')
        stok_minimum = request.form.get('stok_minimum')
        harga = request.form.get('harga')

        obat = Obat(
            nama=nama,
            kode=kode,
            jenis=jenis,
            dosis=dosis,
            satuan=satuan,
            stok=stok or 0,
            stok_minimum=stok_minimum or 10,
            harga=harga or 0,
            aktif=True
        )

        db.session.add(obat)
        db.session.commit()

        flash('Obat berhasil ditambahkan!', 'success')
        return redirect(url_for('farmasi.obat'))

    return render_template('farmasi/obat_baru.html')

@farmasi_bp.route('/obat/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def obat_edit(id):
    obat = Obat.query.get_or_404(id)

    if request.method == 'POST':
        obat.nama = request.form.get('nama')
        obat.kode = request.form.get('kode')
        obat.jenis = request.form.get('jenis')
        obat.dosis = request.form.get('dosis')
        obat.satuan = request.form.get('satuan')
        obat.stok = request.form.get('stok')
        obat.stok_minimum = request.form.get('stok_minimum')
        obat.harga = request.form.get('harga')

        db.session.commit()
        flash('Obat berhasil diperbarui!', 'success')
        return redirect(url_for('farmasi.obat'))

    return render_template('farmasi/obat_edit.html', obat=obat)

@farmasi_bp.route('/obat/<int:id>/delete', methods=['POST'])
@login_required
def obat_delete(id):
    obat = Obat.query.get_or_404(id)
    obat.aktif = False
    db.session.commit()
    flash('Obat berhasil dihapus!', 'success')
    return redirect(url_for('farmasi.obat'))

@farmasi_bp.route('/stok-rendah')
@login_required
def stok_rendah():
    """Lihat obat dengan stok rendah"""
    obat_list = Obat.query.filter(
        Obat.stok <= Obat.stok_minimum,
        Obat.aktif == True
    ).order_by(Obat.stok).all()

    return render_template('farmasi/stok_rendah.html', obat_list=obat_list)

# Resep and ResepDetail are now imported from models.py

@farmasi_bp.route('/resep')
@login_required
def resep():
    status = request.args.get('status', '')

    query = Resep.query

    if status:
        query = query.filter_by(status=status)
    else:
        query = query.filter_by(status='menunggu')

    resep_list = query.order_by(Resep.tanggal.desc()).all()

    return render_template('farmasi/resep.html',
                         resep_list=resep_list,
                         status=status)

@farmasi_bp.route('/resep/baru', methods=['GET', 'POST'])
@login_required
def resep_baru():
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        obat_ids = request.form.getlist('obat_id[]')
        jumlahs = request.form.getlist('jumlah[]')
        dosiss = request.form.getlist('dosis[]')
        catatan = request.form.get('catatan')

        # Create resep
        resep = Resep(
            pasien_id=pasien_id,
            dokter_id=current_user.id,
            catatan=catatan,
            status='menunggu'
        )
        db.session.add(resep)
        db.session.flush()

        # Create resep details
        for obat_id, jumlah, dosis in zip(obat_ids, jumlahs, dosiss):
            if obat_id and jumlah:
                detail = ResepDetail(
                    resep_id=resep.id,
                    obat_id=obat_id,
                    jumlah=jumlah,
                    dosis=dosis
                )
                db.session.add(detail)

        db.session.commit()

        flash('Resep berhasil dibuat!', 'success')
        return redirect(url_for('farmasi.resep'))

    pasien_list = Pasien.query.filter_by(aktif=True).all()
    obat_list = Obat.query.filter_by(aktif=True).all()

    return render_template('farmasi/resep_baru.html',
                         pasien_list=pasien_list,
                         obat_list=obat_list)

@farmasi_bp.route('/resep/<int:id>')
@login_required
def resep_detail(id):
    resep = Resep.query.get_or_404(id)
    return render_template('farmasi/resep_detail.html', resep=resep)

@farmasi_bp.route('/resep/<int:id>/selesai', methods=['POST'])
@login_required
def resep_selesai(id):
    """Proses resep - kurangi stok obat"""
    resep = Resep.query.get_or_404(id)

    for detail in resep.details:
        obat = detail.obat
        if obat.stok >= detail.jumlah:
            obat.stok -= detail.jumlah
        else:
            flash(f'Stok {obat.nama} tidak cukup!', 'danger')
            return redirect(url_for('farmasi.resep_detail', id=resep.id))

    resep.status = 'selesai'
    db.session.commit()

    flash('Resep selesai diproses! Stok obat dikurangi.', 'success')
    return redirect(url_for('farmasi.resep'))
