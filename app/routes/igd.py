from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import IGD, Pasien, User, RawatInap, TempatTidur
from datetime import datetime

igd_bp = Blueprint('igd', __name__, url_prefix='/igd')

@igd_bp.route('/')
@login_required
def index():
    status = request.args.get('status', '')

    query = IGD.query

    if status:
        query = query.filter_by(status=status)
    else:
        query = query.filter_by(status='aktif')

    igd_list = query.order_by(IGD.waktu_masuk.desc()).all()

    return render_template('igd/index.html',
                         igd_list=igd_list,
                         status=status)

@igd_bp.route('/baru', methods=['GET', 'POST'])
@login_required
def baru():
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        keluhan_utama = request.form.get('keluhan_utama')
        triage = request.form.get('triage')

        igd = IGD(
            pasien_id=pasien_id,
            keluhan_utama=keluhan_utama,
            triage=triage,
            waktu_masuk=datetime.now(),
            status='aktif'
        )

        db.session.add(igd)
        db.session.commit()

        flash('Pasien berhasil didaftarkan ke IGD!', 'success')
        return redirect(url_for('igd.index'))

    pasien_list = Pasien.query.filter_by(aktif=True).all()
    return render_template('igd/baru.html', pasien_list=pasien_list)

@igd_bp.route('/<int:id>')
@login_required
def detail(id):
    igd = IGD.query.get_or_404(id)
    return render_template('igd/detail.html', igd=igd)

@igd_bp.route('/<int:id>/periksa', methods=['GET', 'POST'])
@login_required
def periksa(id):
    igd = IGD.query.get_or_404(id)

    if request.method == 'POST':
        igd.diagnose_awal = request.form.get('diagnose_awal')
        igd.tindakan = request.form.get('tindakan')
        igd.dokter_id = current_user.id

        db.session.commit()
        flash('Pemeriksaan IGD selesai!', 'success')
        return redirect(url_for('igd.detail', id=igd.id))

    return render_template('igd/periksa.html', igd=igd)

@igd_bp.route('/<int:id>/rawat-inap', methods=['GET', 'POST'])
@login_required
def konversi_rawat_inap(id):
    """Konversi pasien IGD ke rawat inap"""
    igd = IGD.query.get_or_404(id)

    if request.method == 'POST':
        kamar_id = request.form.get('kamar_id')
        tempat_tidur_id = request.form.get('tempat_tidur_id')
        diagnosa_masuk = request.form.get('diagnosa_masuk')

        # Update tempat tidur
        if tempat_tidur_id:
            tt = TempatTidur.query.get(tempat_tidur_id)
            if tt:
                tt.status = 'occupied'

        # Create rawat inap
        rawat_inap = RawatInap(
            pasien_id=igd.pasien_id,
            kamar_id=kamar_id,
            tempat_tidur_id=tempat_tidur_id,
            diagnosa_masuk=diagnosa_masuk,
            tanggal_masuk=datetime.now(),
            status='aktif'
        )

        # Update IGD status
        igd.status = 'rawat_inap'
        igd.waktu_keluar = datetime.now()

        db.session.add(rawat_inap)
        db.session.commit()

        flash('Pasien dikonversi ke Rawat Inap!', 'success')
        return redirect(url_for('rawat_inap.index'))

    from app.models import Kamar
    kamar_list = Kamar.query.filter_by(aktif=True).all()
    return render_template('igd/konversi_rawat_inap.html', igd=igd, kamar_list=kamar_list)

@igd_bp.route('/<int:id>/pulang', methods=['GET', 'POST'])
@login_required
def pulang(id):
    igd = IGD.query.get_or_404(id)

    if request.method == 'POST':
        igd.status = 'pulang'
        igd.waktu_keluar = datetime.now()
        igd.tindakan = request.form.get('tindakan')

        db.session.commit()
        flash('Pasien dipulangkan dari IGD!', 'success')
        return redirect(url_for('igd.index'))

    return render_template('igd/pulang.html', igd=igd)
