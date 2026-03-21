from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import KamarOK, Operasi, JadwalOK, Pasien, User
from datetime import datetime, date, time

ok_bp = Blueprint('ok', __name__, url_prefix='/ok')


@ok_bp.route('/')
@login_required
def index():
    """List jadwal operasi hari ini dan yg akan datang"""
    today = date.today()
    status_filter = request.args.get('status', '')

    query = Operasi.query

    if status_filter:
        query = query.filter(Operasi.status == status_filter)
    else:
        # Default: show terjadwal and proses
        query = query.filter(Operasi.status.in_(['terjadwal', 'proses']))

    operasi_list = query.order_by(Operasi.tanggal_operasi).all()
    return render_template('ok/index.html', operasi_list=operasi_list, status_filter=status_filter)


@ok_bp.route('/baru', methods=['GET', 'POST'])
@login_required
def baru():
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        tanggal_operasi = request.form.get('tanggal_operasi')
        jam_mulai = request.form.get('jam_mulai')
        jam_selesai = request.form.get('jam_selesai')
        kamar_ok_id = request.form.get('kamar_ok_id')
        diagnosis = request.form.get('diagnosis')
        prosedur = request.form.get('prosedur')
        dokter_surgeon_id = request.form.get('dokter_surgeon_id')
        dokter_anestesi_id = request.form.get('dokter_anestesi_id')
        catatan = request.form.get('catatan')

        # Generate no_operasi
        last_op = Operasi.query.order_by(Operasi.id.desc()).first()
        if last_op and last_op.no_operasi:
            last_num = int(last_op.no_operasi.split('-')[-1])
            no_operasi = f'OK-{last_num + 1:04d}'
        else:
            no_operasi = 'OK-0001'

        operasi = Operasi(
            pasien_id=pasien_id,
            no_operasi=no_operasi,
            tanggal_operasi=datetime.strptime(f'{tanggal_operasi} {jam_mulai}', '%Y-%m-%d %H:%M'),
            diagnosis=diagnosis,
            prosedur=prosedur,
            dokter_surgeon_id=dokter_surgeon_id,
            dokter_anestesi_id=dokter_anestesi_id,
            catatan=catatan
        )
        db.session.add(operasi)
        db.session.commit()

        # Create jadwal OK
        if kamar_ok_id:
            jadwal_ok = JadwalOK(
                operasi_id=operasi.id,
                kamar_ok_id=kamar_ok_id,
                tanggal=datetime.strptime(tanggal_operasi, '%Y-%m-%d').date(),
                jam_mulai=datetime.strptime(jam_mulai, '%H:%M').time(),
                jam_selesai=datetime.strptime(jam_selesai, '%H:%M').time()
            )
            db.session.add(jadwal_ok)
            db.session.commit()

        flash('Jadwal operasi berhasil dibuat', 'success')
        return redirect(url_for('ok.index'))

    pasien_list = Pasien.query.filter(Pasien.aktif == True).all()
    dokter_list = User.query.filter(User.role == 'dokter').all()
    kamar_list = KamarOK.query.filter(KamarOK.aktif == True).all()
    return render_template('ok/baru.html', pasien_list=pasien_list, dokter_list=dokter_list, kamar_list=kamar_list)


@ok_bp.route('/<int:id>')
@login_required
def detail(id):
    operasi = Operasi.query.get_or_404(id)
    return render_template('ok/detail.html', operasi=operasi)


@ok_bp.route('/<int:id>/update-status', methods=['POST'])
@login_required
def update_status(id):
    operasi = Operasi.query.get_or_404(id)
    new_status = request.form.get('status')

    operasi.status = new_status
    db.session.commit()

    flash(f'Status operasi diperbarui menjadi {new_status}', 'success')
    return redirect(url_for('ok.detail', id=id))


@ok_bp.route('/<int:id>/batal', methods=['POST'])
@login_required
def batal(id):
    operasi = Operasi.query.get_or_404(id)
    operasi.status = 'batal'
    db.session.commit()

    flash('Operasi dibatalkan', 'success')
    return redirect(url_for('ok.index'))


@ok_bp.route('/kamar')
@login_required
def kamar_list():
    kamar_list = KamarOK.query.all()
    return render_template('ok/kamar_list.html', kamar_list=kamar_list)


@ok_bp.route('/kamar/baru', methods=['GET', 'POST'])
@login_required
def kamar_baru():
    if request.method == 'POST':
        nama = request.form.get('nama')
        lokasi = request.form.get('lokasi')
        kapasitas = int(request.form.get('kapasitas', 1))
        peralatan = request.form.get('peralatan')

        kamar = KamarOK(
            nama=nama,
            lokasi=lokasi,
            kapasitas=kapasitas,
            peralatan=peralatan
        )
        db.session.add(kamar)
        db.session.commit()

        flash('Kamar OK berhasil ditambahkan', 'success')
        return redirect(url_for('ok.kamar_list'))

    return render_template('ok/kamar_baru.html')


@ok_bp.route('/kamar/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def kamar_edit(id):
    kamar = KamarOK.query.get_or_404(id)

    if request.method == 'POST':
        kamar.nama = request.form.get('nama')
        kamar.lokasi = request.form.get('lokasi')
        kamar.kapasitas = int(request.form.get('kapasitas', 1))
        kamar.peralatan = request.form.get('peralatan')
        kamar.aktif = 'aktif' in request.form

        db.session.commit()
        flash('Kamar OK diperbarui', 'success')
        return redirect(url_for('ok.kamar_list'))

    return render_template('ok/kamar_edit.html', kamar=kamar)


@ok_bp.route('/api/available')
@login_required
def api_available():
    """JSON: cek ketersediaan kamar OK"""
    tanggal = request.args.get('tanggal', date.today())

    kamar_list = KamarOK.query.filter(KamarOK.aktif == True).all()
    available = []

    for kamar in kamar_list:
        # Check if kamar is booked on the date
        booked = JadwalOK.query.filter_by(kamar_ok_id=kamar.id, tanggal=tanggal).first()
        if not booked:
            available.append({
                'id': kamar.id,
                'nama': kamar.nama,
                'lokasi': kamar.lokasi
            })

    return jsonify({'available': available})