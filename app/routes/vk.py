from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import KamarVK, Persalinan, Pasien, User, RegistrasiKehilangan, PemeriksaanKehilangan
from datetime import datetime, date

vk_bp = Blueprint('vk', __name__, url_prefix='/vk')


@vk_bp.route('/')
@login_required
def index():
    """Dashboard VK (kamar bersalin)"""
    # Summary
    kamar_tersedia = KamarVK.query.filter_by(status='tersedia').count()
    kamar_occupied = KamarVK.query.filter_by(status='occupied').count()

    # Persalinan hari ini
    today = date.today()
    persalinan_hari_ini = Persalinan.query.filter(
        db.func.date(Persalinan.tanggal_persalinan) == today
    ).count()

    # Persalinan dalam proses
    dalam_proses = Persalinan.query.filter_by(status='dalam_proses').count()

    return render_template('vk/index.html',
                         kamar_tersedia=kamar_tersedia,
                         kamar_occupied=kamar_occupied,
                         persalinan_hari_ini=persalinan_hari_ini,
                         dalam_proses=dalam_proses)


@vk_bp.route('/kamar')
@login_required
def kamar_list():
    kamar_list = KamarVK.query.all()
    return render_template('vk/kamar_list.html', kamar_list=kamar_list)


@vk_bp.route('/kamar/baru', methods=['GET', 'POST'])
@login_required
def kamar_baru():
    if request.method == 'POST':
        nama = request.form.get('nama')
        kapasitas = int(request.form.get('kapasitas', 1))
        fasilitas = request.form.get('fasilitas')

        kamar = KamarVK(
            nama=nama,
            kapasitas=kapasitas,
            fasilitas=fasilitas
        )
        db.session.add(kamar)
        db.session.commit()

        flash('Kamar VK berhasil ditambahkan', 'success')
        return redirect(url_for('vk.kamar_list'))

    return render_template('vk/kamar_baru.html')


@vk_bp.route('/kamar/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def kamar_edit(id):
    kamar = KamarVK.query.get_or_404(id)

    if request.method == 'POST':
        kamar.nama = request.form.get('nama')
        kamar.kapasitas = int(request.form.get('kapasitas', 1))
        kamar.fasilitas = request.form.get('fasilitas')
        kamar.status = request.form.get('status')
        kamar.aktif = 'aktif' in request.form

        db.session.commit()
        flash('Kamar VK diperbarui', 'success')
        return redirect(url_for('vk.kamar_list'))

    return render_template('vk/kamar_edit.html', kamar=kamar)


@vk_bp.route('/persalinan')
@login_required
def persalinan_list():
    status_filter = request.args.get('status', '')

    query = Persalinan.query

    if status_filter:
        query = query.filter(Persalinan.status == status_filter)

    persalinan_list = query.order_by(Persalinan.tanggal_persalinan.desc()).all()
    return render_template('vk/persalinan_list.html', persalinan_list=persalinan_list, status_filter=status_filter)


@vk_bp.route('/persalinan/baru', methods=['GET', 'POST'])
@login_required
def persalinan_baru():
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        kamar_vk_id = request.form.get('kamar_vk_id')
        tanggal_masuk = request.form.get('tanggal_masuk')
        jenis_persalinan = request.form.get('jenis_persalinan')
        diagnosis = request.form.get('diagnosis')
        dokter_id = request.form.get('dokter_id')
        bidan_id = request.form.get('bidan_id')
        catatan = request.form.get('catatan')

        # Generate no_persalinan
        last_persalinan = Persalinan.query.order_by(Persalinan.id.desc()).first()
        if last_persalinan and last_persalinan.no_persalinan:
            last_num = int(last_persalinan.no_persalinan.split('-')[-1])
            no_persalinan = f'VK-{last_num + 1:04d}'
        else:
            no_persalinan = 'VK-0001'

        persalinan = Persalinan(
            pasien_id=pasien_id,
            no_persalinan=no_persalinan,
            kamar_vk_id=kamar_vk_id,
            tanggal_masuk=datetime.strptime(tanggal_masuk, '%Y-%m-%d %H:%M') if tanggal_masuk else datetime.now(),
            jenis_persalinan=jenis_persalinan,
            diagnosis=diagnosis,
            dokter_id=dokter_id,
            bidan_id=bidan_id,
            catatan=catatan,
            status='dalam_proses'
        )
        db.session.add(persalinan)

        # Update kamar VK status
        if kamar_vk_id:
            kamar = KamarVK.query.get(kamar_vk_id)
            if kamar:
                kamar.status = 'occupied'

        db.session.commit()

        flash('Data persalinan berhasil disimpan', 'success')
        return redirect(url_for('vk.persalinan_list'))

    pasien_list = Pasien.query.filter(Pasien.aktif == True).all()
    kamar_list = KamarVK.query.filter(KamarVK.status == 'tersedia', KamarVK.aktif == True).all()
    dokter_list = User.query.filter(User.role == 'dokter').all()
    bidan_list = User.query.filter(User.role == 'bidan').all()
    return render_template('vk/persalinan_baru.html', pasien_list=pasien_list, kamar_list=kamar_list,
                         dokter_list=dokter_list, bidan_list=bidan_list)


@vk_bp.route('/persalinan/<int:id>')
@login_required
def persalinan_detail(id):
    persalinan = Persalinan.query.get_or_404(id)
    return render_template('vk/persalinan_detail.html', persalinan=persalinan)


@vk_bp.route('/persalinan/<int:id>/update-status', methods=['POST'])
@login_required
def persalinan_update_status(id):
    persalinan = Persalinan.query.get_or_404(id)

    persalinan.status = request.form.get('status')
    persalinan.tanggal_persalinan = datetime.now() if request.form.get('status') == 'selesai' else persalinan.tanggal_persalinan
    persalinan.kondisi_ibu = request.form.get('kondisi_ibu', persalinan.kondisi_ibu)
    persalinan.kondisi_bayi = request.form.get('kondisi_bayi', persalinan.kondisi_bayi)
    persalinan.berat_bayi = request.form.get('berat_bayi', persalinan.berat_bayi)
    persalinan.jk_bayi = request.form.get('jk_bayi', persalinan.jk_bayi)

    # Update kamar VK status
    if persalinan.status == 'selesai' and persalinan.kamar_vk_id:
        kamar = KamarVK.query.get(persalinan.kamar_vk_id)
        if kamar:
            kamar.status = 'cleaning'

    db.session.commit()
    flash('Status persalinan diperbarui', 'success')
    return redirect(url_for('vk.persalinan_detail', id=id))


@vk_bp.route('/kehilangan')
@login_required
def kehamilan_list():
    """List registrasi kehamilan (ANC)"""
    kehamilan_list = RegistrasiKehilangan.query.filter(RegistrasiKehilangan.aktif == True).order_by(
        RegistrasiKehilangan.tanggal_registrasi.desc()
    ).all()
    return render_template('vk/kehilangan_list.html', kehamilan_list=kehilangan_list)


@vk_bp.route('/kehilangan/baru', methods=['GET', 'POST'])
@login_required
def kehilangan_baru():
    """Registrasi ibu hamil baru"""
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        taksiran_persalinan = request.form.get('taksiran_persalinan')
        risiko_kehilangan = request.form.get('risiko_kehilangan')
        tenaga_penolong = request.form.get('tenaga_penolong')

        # Generate no_registrasi
        last_reg = RegistrasiKehilangan.query.order_by(RegistrasiKehilangan.id.desc()).first()
        if last_reg and last_reg.no_registrasi:
            last_num = int(last_reg.no_registrasi.split('-')[-1])
            no_registrasi = f'ANC-{last_num + 1:04d}'
        else:
            no_registrasi = 'ANC-0001'

        registrasi = RegistrasiKehilangan(
            pasien_id=pasien_id,
            no_registrasi=no_registrasi,
            taksiran_persalinan=datetime.strptime(taksiran_persalinan, '%Y-%m-%d').date() if taksiran_persalinan else None,
            risiko_kehilangan=risiko_kehilangan,
            tenaga_penolong=tenaga_penolong
        )
        db.session.add(registrasi)
        db.session.commit()

        flash('Registrasi ibu hamil berhasil', 'success')
        return redirect(url_for('vk.kehilangan_list'))

    pasien_list = Pasien.query.filter(Pasien.aktif == True).all()
    return render_template('vk/kehilangan_baru.html', pasien_list=pasien_list)


@vk_bp.route('/kehilangan/<int:id>/pemeriksaan')
@login_required
def pemeriksaan_anc(id):
    """List pemeriksaan ANC untuk satu registrasi"""
    registrasi = RegistrasiKehilangan.query.get_or_404(id)
    pemeriksaan_list = PemeriksaanKehilangan.query.filter_by(
        registrasi_kehilangan_id=id
    ).order_by(PemeriksaanKehilangan.tanggal_periksa.desc()).all()
    return render_template('vk/pemeriksaan_anc.html', registrasi=registrasi, pemeriksaan_list=pemeriksaan_list)


@vk_bp.route('/kehilangan/<int:id>/pemeriksaan/baru', methods=['GET', 'POST'])
@login_required
def pemeriksaan_anc_baru(id):
    """Input pemeriksaan ANC baru"""
    registrasi = RegistrasiKehilangan.query.get_or_404(id)

    if request.method == 'POST':
        trimester = request.form.get('trimester')
        berat_badan = request.form.get('berat_badan')
        tekanan_darah = request.form.get('tekanan_darah')
        tinggi_fundus = request.form.get('tinggi_fundus')
        detak_jantung_janin = request.form.get('detak_jantung_janin')
        diagnosis = request.form.get('diagnosis')
        catatan = request.form.get('catatan')

        pemeriksaan = PemeriksaanKehilangan(
            registrasi_kehilangan_id=id,
            pasien_id=registrasi.pasien_id,
            trimester=int(trimester) if trimester else None,
            berat_badan=berat_badan,
            tekanan_darah=tekanan_darah,
            tinggi_fundus=tinggi_fundus,
            detak_jantung_janin=int(detik_jantung_janin) if detak_jantung_janin else None,
            diagnosis=diagnosis,
            catatan=catatan
        )
        db.session.add(pemeriksaan)
        db.session.commit()

        flash('Pemeriksaan ANC berhasil disimpan', 'success')
        return redirect(url_for('vk.pemeriksaan_anc', id=id))

    return render_template('vk/pemeriksaan_anc_baru.html', registrasi=registrasi)