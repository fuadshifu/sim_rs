from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import RawatInap, Pasien, Kamar, TempatTidur, User
from datetime import datetime

rawat_inap_bp = Blueprint('rawat_inap', __name__, url_prefix='/rawat-inap')

@rawat_inap_bp.route('/')
@login_required
def index():
    status = request.args.get('status', '')
    kelas = request.args.get('kelas', '')

    query = RawatInap.query

    if status:
        query = query.filter_by(status=status)
    if kelas:
        query = query.join(Kamar).filter(Kamar.kelas == kelas)

    rawat_inap_list = query.order_by(RawatInap.tanggal_masuk.desc()).all()

    return render_template('rawat_inap/index.html',
                         rawat_inap_list=rawat_inap_list,
                         status=status,
                         kelas=kelas)

@rawat_inap_bp.route('/baru', methods=['GET', 'POST'])
@login_required
def baru():
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        kamar_id = request.form.get('kamar_id')
        tempat_tidur_id = request.form.get('tempat_tidur_id')
        diagnosa_masuk = request.form.get('diagnosa_masuk')

        # Update tempat tidur status
        if tempat_tidur_id:
            tt = TempatTidur.query.get(tempat_tidur_id)
            if tt:
                tt.status = 'occupied'

        rawat_inap = RawatInap(
            pasien_id=pasien_id,
            kamar_id=kamar_id,
            tempat_tidur_id=tempat_tidur_id,
            diagnosa_masuk=diagnosa_masuk,
            tanggal_masuk=datetime.now(),
            status='aktif'
        )

        db.session.add(rawat_inap)
        db.session.commit()

        flash('Pasien berhasil di rawat inap!', 'success')
        return redirect(url_for('rawat_inap.index'))

    pasien_list = Pasien.query.filter_by(aktif=True).all()
    kamar_list = Kamar.query.filter_by(aktif=True).all()

    return render_template('rawat_inap/baru.html',
                         pasien_list=pasien_list,
                         kamar_list=kamar_list)

@rawat_inap_bp.route('/<int:id>')
@login_required
def detail(id):
    rawat_inap = RawatInap.query.get_or_404(id)
    return render_template('rawat_inap/detail.html', rawat_inap=rawat_inap)

@rawat_inap_bp.route('/<int:id>/pulang', methods=['GET', 'POST'])
@login_required
def pulang(id):
    rawat_inap = RawatInap.query.get_or_404(id)

    if request.method == 'POST':
        rawat_inap.tanggal_keluar = datetime.now()
        rawat_inap.diagnosa_utama = request.form.get('diagnosa_utama')
        rawat_inap.status = 'keluar'

        # Free the bed
        if rawat_inap.tempat_tidur_id:
            tt = TempatTidur.query.get(rawat_inap.tempat_tidur_id)
            if tt:
                tt.status = 'tersedia'

        db.session.commit()
        flash('Pasien dipulangkan!', 'success')
        return redirect(url_for('rawat_inap.index'))

    return render_template('rawat_inap/pulang.html', rawat_inap=rawat_inap)

@rawat_inap_bp.route('/get-tempat-tidur/<int:kamar_id>')
@login_required
def get_tempat_tidur(kamar_id):
    """API untuk mendapatkan tempat tidur yang tersedia di kamar tertentu"""
    tt_list = TempatTidur.query.filter_by(kamar_id=kamar_id, status='tersedia', aktif=True).all()
    return {'results': [{'id': tt.id, 'nomor': tt.nomor} for tt in tt_list]}
