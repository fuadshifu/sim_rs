from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import RekamMedis, Pasien, RawatJalan, RawatInap, IGD
from datetime import datetime

rekam_medis_bp = Blueprint('rekam_medis', __name__, url_prefix='/rekam-medis')

@rekam_medis_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '')
    pasien_id = request.args.get('pasien_id', '')

    query = RekamMedis.query

    if search:
        query = query.join(Pasien).filter(
            (Pasien.nik.like(f'%{search}%')) |
            (Pasien.nama_lengkap.like(f'%{search}%'))
        )
    if pasien_id:
        query = query.filter_by(pasien_id=pasien_id)

    rekam_medis_list = query.order_by(RekamMedis.tanggal.desc()).all()

    return render_template('rekam_medis/index.html',
                         rekam_medis_list=rekam_medis_list,
                         search=search,
                         pasien_id=pasien_id)

@rekam_medis_bp.route('/pasien/<int:pasien_id>')
@login_required
def pasien(pasien_id):
    """Lihat rekam medis pasien tertentu"""
    pasien = Pasien.query.get_or_404(pasien_id)
    rm_list = RekamMedis.query.filter_by(pasien_id=pasien_id).order_by(RekamMedis.tanggal.desc()).all()

    return render_template('rekam_medis/pasien.html', pasien=pasien, rm_list=rm_list)

@rekam_medis_bp.route('/<int:id>')
@login_required
def detail(id):
    rm = RekamMedis.query.get_or_404(id)
    return render_template('rekam_medis/detail.html', rm=rm)

@rekam_medis_bp.route('/baru', methods=['GET', 'POST'])
@login_required
def baru():
    """Buat rekam medis baru dari layanan (rawat jalan/inap/igd)"""
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        layanan_id = request.form.get('layanan_id')
        jenis_layanan = request.form.get('jenis_layanan')
        subjective = request.form.get('subjective')
        objective = request.form.get('objective')
        assessment = request.form.get('assessment')
        plan = request.form.get('plan')

        rm = RekamMedis(
            pasien_id=pasien_id,
            dokter_id=current_user.id,
            layanan_id=layanan_id,
            jenis_layanan=jenis_layanan,
            subjective=subjective,
            objective=objective,
            assessment=assessment,
            plan=plan,
            tanggal=datetime.now()
        )

        db.session.add(rm)
        db.session.commit()

        flash('Rekam medis berhasil dibuat!', 'success')
        return redirect(url_for('rekam_medis.index'))

    pasien_id = request.args.get('pasien_id')
    jenis_layanan = request.args.get('jenis_layanan')
    layanan_id = request.args.get('layanan_id')

    pasien_list = Pasien.query.filter_by(aktif=True).all()

    return render_template('rekam_medis/baru.html',
                         pasien_list=pasien_list,
                         pasien_id=pasien_id,
                         jenis_layanan=jenis_layanan,
                         layanan_id=layanan_id)

@rekam_medis_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    rm = RekamMedis.query.get_or_404(id)

    if request.method == 'POST':
        rm.subjective = request.form.get('subjective')
        rm.objective = request.form.get('objective')
        rm.assessment = request.form.get('assessment')
        rm.plan = request.form.get('plan')

        db.session.commit()
        flash('Rekam medis berhasil diperbarui!', 'success')
        return redirect(url_for('rekam_medis.detail', id=rm.id))

    return render_template('rekam_medis/edit.html', rm=rm)
