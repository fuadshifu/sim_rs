from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response
from flask_login import login_required, current_user
from app import db
from app.models import RekamMedis, Pasien, RawatJalan, RawatInap, IGD, ResumeMedis, SuratSakit, Consent
from datetime import datetime, date

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

# ==================== RESUME MEDIS ====================

@rekam_medis_bp.route('/resume/<int:pasien_id>')
@login_required
def resume_list(pasien_id):
    """Lihat resume medis pasien"""
    pasien = Pasien.query.get_or_404(pasien_id)
    resume_list = ResumeMedis.query.filter_by(pasien_id=pasien_id).order_by(ResumeMedis.tanggal_keluar.desc()).all()
    return render_template('rekam_medis/resume_list.html', pasien=pasien, resume_list=resume_list)

@rekam_medis_bp.route('/resume/baru', methods=['GET', 'POST'])
@login_required
def resume_baru():
    """Buat resume medis baru"""
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        layanan_jenis = request.form.get('layanan_jenis')
        layanan_id = request.form.get('layanan_id')
        tanggal_masuk = request.form.get('tanggal_masuk')
        tanggal_keluar = request.form.get('tanggal_keluar')
        diagnosa_utama = request.form.get('diagnosa_utama')
        diagnosa_sekunder = request.form.get('diagnosa_sekunder')
        prosedur = request.form.get('prosedur')
        icd9_ids = request.form.get('icd9_ids')
        kondisi_keluar = request.form.get('kondisi_keluar')
        obat_pulang = request.form.get('obat_pulang')
        kontrol_ulang = request.form.get('kontrol_ulang')

        resume = ResumeMedis(
            pasien_id=pasien_id,
            layanan_jenis=layanan_jenis,
            layanan_id=layanan_id,
            tanggal_masuk=datetime.strptime(tanggal_masuk, '%Y-%m-%d').date() if tanggal_masuk else None,
            tanggal_keluar=datetime.strptime(tanggal_keluar, '%Y-%m-%d').date() if tanggal_keluar else None,
            diagnosa_utama=diagnosa_utama,
            diagnosa_sekunder=diagnosa_sekunder,
            prosedur=prosedur,
            icd9_ids=icd9_ids,
            kondisi_keluar=kondisi_keluar,
            obat_pulang=obat_pulang,
            kontrol_ulang=kontrol_ulang,
            dokter_id=current_user.id
        )

        db.session.add(resume)
        db.session.commit()

        flash('Resume medis berhasil dibuat!', 'success')
        return redirect(url_for('rekam_medis.resume_list', pasien_id=pasien_id))

    pasien_id = request.args.get('pasien_id')
    pasien_list = Pasien.query.filter_by(aktif=True).all()

    return render_template('rekam_medis/resume_baru.html', pasien_list=pasien_list, pasien_id=pasien_id)

@rekam_medis_bp.route('/resume/<int:id>')
@login_required
def resume_detail(id):
    """Detail resume medis"""
    resume = ResumeMedis.query.get_or_404(id)
    return render_template('rekam_medis/resume_detail.html', resume=resume)

# ==================== SURAT KETERANGAN SAKIT ====================

@rekam_medis_bp.route('/surat-sakit')
@login_required
def surat_sakit_list():
    """Daftar surat keterangan sakit"""
    status_filter = request.args.get('status', '')

    query = SuratSakit.query
    if status_filter:
        query = query.filter_by(status=status_filter)

    surat_list = query.order_by(SuratSakit.tanggal_surat.desc()).all()
    return render_template('rekam_medis/surat_sakit_list.html', surat_list=surat_list)

@rekam_medis_bp.route('/surat-sakit/baru', methods=['GET', 'POST'])
@login_required
def surat_sakit_baru():
    """Buat surat keterangan sakit"""
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        diagnosa = request.form.get('diagnosa')
        lama_sakit = request.form.get('lama_sakit')
        mulai_tanggal = request.form.get('mulai_tanggal')
        sampai_tanggal = request.form.get('sampai_tanggal')
        catatan = request.form.get('catatan')

        surat = SuratSakit(
            pasien_id=pasien_id,
            diagnosa=diagnosa,
            lama_sakit=lama_sakit,
            mulai_tanggal=datetime.strptime(mulai_tanggal, '%Y-%m-%d').date() if mulai_tanggal else None,
            sampai_tanggal=datetime.strptime(sampai_tanggal, '%Y-%m-%d').date() if sampai_tanggal else None,
            dokter_id=current_user.id,
            catatan=catatan
        )

        db.session.add(surat)
        db.session.commit()

        flash('Surat keterangan sakit berhasil dibuat!', 'success')
        return redirect(url_for('rekam_medis.surat_sakit_list'))

    pasien_id = request.args.get('pasien_id')
    pasien_list = Pasien.query.filter_by(aktif=True).all()

    return render_template('rekam_medis/surat_sakit_baru.html', pasien_list=pasien_list, pasien_id=pasien_id)

@rekam_medis_bp.route('/surat-sakit/<int:id>')
@login_required
def surat_sakit_detail(id):
    """Detail surat keterangan sakit"""
    surat = SuratSakit.query.get_or_404(id)
    return render_template('rekam_medis/surat_sakit_detail.html', surat=surat)

@rekam_medis_bp.route('/surat-sakit/<int:id>/print')
@login_required
def surat_sakit_print(id):
    """Print surat keterangan sakit"""
    surat = SuratSakit.query.get_or_404(id)

    # Render template ke HTML
    html = render_template('rekam_medis/surat_sakit_print.html', surat=surat)

    # Create PDF response (using make_response for HTML for now)
    response = make_response(html)
    response.headers['Content-Type'] = 'text/html'
    return response

@rekam_medis_bp.route('/surat-sakit/<int:id>/use')
@login_required
def surat_sakit_use(id):
    """Tandai surat sakit sudah digunakan"""
    surat = SuratSakit.query.get_or_404(id)
    surat.status = 'used'
    db.session.commit()

    flash('Surat keterangan sakit ditandai sudah digunakan', 'success')
    return redirect(url_for('rekam_medis.surat_sakit_detail', id=id))

# ==================== CONSENT (SETUJU TINDAKAN) ====================

@rekam_medis_bp.route('/consent')
@login_required
def consent_list():
    """Daftar consent"""
    status_filter = request.args.get('status', '')

    query = Consent.query
    if status_filter:
        query = query.filter_by(status=status_filter)

    consent_list = query.order_by(Consent.tanggal_consent.desc()).all()
    return render_template('rekam_medis/consent_list.html', consent_list=consent_list)

@rekam_medis_bp.route('/consent/baru', methods=['GET', 'POST'])
@login_required
def consent_baru():
    """Buat consent baru"""
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        tindakan = request.form.get('tindakan')
        status = request.form.get('status')
        catatan = request.form.get('catatan')

        consent = Consent(
            pasien_id=pasien_id,
            tindakan=tindakan,
            dokter_id=current_user.id,
            status=status,
            catatan=catatan
        )

        db.session.add(consent)
        db.session.commit()

        flash('Consent berhasil dibuat!', 'success')
        return redirect(url_for('rekam_medis.consent_list'))

    pasien_id = request.args.get('pasien_id')
    pasien_list = Pasien.query.filter_by(aktif=True).all()

    return render_template('rekam_medis/consent_baru.html', pasien_list=pasien_list, pasien_id=pasien_id)

@rekam_medis_bp.route('/consent/<int:id>')
@login_required
def consent_detail(id):
    """Detail consent"""
    consent = Consent.query.get_or_404(id)
    return render_template('rekam_medis/consent_detail.html', consent=consent)

@rekam_medis_bp.route('/consent/<int:id>/update-status', methods=['POST'])
@login_required
def consent_update_status(id):
    """Update status consent"""
    consent = Consent.query.get_or_404(id)
    new_status = request.form.get('status')

    consent.status = new_status
    db.session.commit()

    flash(f'Status consent diperbarui menjadi: {new_status}', 'success')
    return redirect(url_for('rekam_medis.consent_detail', id=id))
