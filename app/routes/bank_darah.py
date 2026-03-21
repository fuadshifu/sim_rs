from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import GolonganDarah, StokDarah, Pendonor, PermintaanDarah, TransaksiDarah, Pasien, User
from datetime import datetime, date, timedelta

bank_darah_bp = Blueprint('bank_darah', __name__, url_prefix='/bank-darah')


@bank_darah_bp.route('/')
@login_required
def index():
    """Dashboard stok darah"""
    # Get summary
    stok_list = StokDarah.query.filter(StokDarah.status == 'tersedia').all()

    # Calculate summary by gol darah
    summary = {}
    for gol in ['A', 'B', 'AB', 'O']:
        gol_obj = GolonganDarah.query.filter_by(nama=gol).first()
        if gol_obj:
            total = sum(s.jumlah for s in gol_obj.stok_darah if s.status == 'tersedia')
            summary[gol] = total

    # Alert: darah mendekati expired (7 hari)
    expired_soon = StokDarah.query.filter(
        StokDarah.status == 'tersedia',
        StokDarah.expire_date <= date.today() + timedelta(days=7)
    ).all()

    return render_template('bank_darah/index.html', stok_list=stok_list, summary=summary, expired_soon=expired_soon)


@bank_darah_bp.route('/stok')
@login_required
def stok_list():
    gol_filter = request.args.get('golongan', '')
    komponen_filter = request.args.get('komponen', '')

    query = StokDarah.query

    if gol_filter:
        gol = GolonganDarah.query.filter_by(nama=gol_filter).first()
        if gol:
            query = query.filter(StokDarah.gol_darah_id == gol.id)

    if komponen_filter:
        query = query.filter(StokDarah.komponen == komponen_filter)

    stok_list = query.order_by(StokDarah.expire_date).all()
    return render_template('bank_darah/stok_list.html', stok_list=stok_list, gol_filter=gol_filter, komponen_filter=komponen_filter)


@bank_darah_bp.route('/stok/tambah', methods=['GET', 'POST'])
@login_required
def stok_tambah():
    if request.method == 'POST':
        gol_darah_id = request.form.get('gol_darah_id')
        komponen = request.form.get('komponen')
        jumlah = int(request.form.get('jumlah', 1))
        expire_date = request.form.get('expire_date')

        # Check if similar stock exists
        existing = StokDarah.query.filter_by(
            gol_darah_id=gol_darah_id,
            komponen=komponen,
            expire_date=expire_date,
            status='tersedia'
        ).first()

        if existing:
            existing.jumlah += jumlah
        else:
            stok = StokDarah(
                gol_darah_id=gol_darah_id,
                komponen=komponen,
                jumlah=jumlah,
                expire_date=expire_date,
                tanggal_masuk=date.today()
            )
            db.session.add(stok)

        db.session.commit()
        flash('Stok darah berhasil ditambahkan', 'success')
        return redirect(url_for('bank_darah.stok_list'))

    gol_darah_list = GolonganDarah.query.filter(GolonganDarah.aktif == True).all()
    komponen_options = ['WB', 'PRC', 'TC', 'FFP', 'Cryo']
    return render_template('bank_darah/stok_tambah.html', gol_darah_list=gol_darah_list, komponen_options=komponen_options)


@bank_darah_bp.route('/pendonor')
@login_required
def pendonor_list():
    search = request.args.get('search', '')
    if search:
        pendonor_list = Pendonor.query.filter(
            Pendonor.nama_lengkap.ilike(f'%{search}%'),
            Pendonor.aktif == True
        ).all()
    else:
        pendonor_list = Pendonor.query.filter(Pendonor.aktif == True).all()
    return render_template('bank_darah/pendonor_list.html', pendonor_list=pendonor_list)


@bank_darah_bp.route('/pendonor/baru', methods=['GET', 'POST'])
@login_required
def pendonor_baru():
    if request.method == 'POST':
        nama_lengkap = request.form.get('nama_lengkap')
        gol_darah_id = request.form.get('gol_darah_id')
        tanggal_lahir = request.form.get('tanggal_lahir')
        jk = request.form.get('jk')
        alamat = request.form.get('alamat')
        no_telepon = request.form.get('no_telepon')

        pendonor = Pendonor(
            nama_lengkap=nama_lengkap,
            gol_darah_id=gol_darah_id,
            tanggal_lahir=tanggal_lahir,
            jk=jk,
            alamat=alamat,
            no_telepon=no_telepon,
            terakhir_donor=date.today()
        )
        db.session.add(pendonor)
        db.session.commit()

        flash('Pendonor berhasil didaftarkan', 'success')
        return redirect(url_for('bank_darah.pendonor_list'))

    gol_darah_list = GolonganDarah.query.filter(GolonganDarah.aktif == True).all()
    return render_template('bank_darah/pendonor_baru.html', gol_darah_list=gol_darah_list)


@bank_darah_bp.route('/permintaan')
@login_required
def permintaan_list():
    status_filter = request.args.get('status', '')
    query = PermintaanDarah.query

    if status_filter:
        query = query.filter(PermintaanDarah.status == status_filter)

    permintaan_list = query.order_by(PermintaanDarah.tanggal_permintaan.desc()).all()
    return render_template('bank_darah/permintaan_list.html', permintaan_list=permintaan_list, status_filter=status_filter)


@bank_darah_bp.route('/permintaan/baru', methods=['GET', 'POST'])
@login_required
def permintaan_baru():
    if request.method == 'POST':
        pasien_id = request.form.get('pasien_id')
        gol_darah_id = request.form.get('gol_darah_id')
        komponen = request.form.get('komponen')
        jumlah = int(request.form.get('jumlah', 1))
        dokter_id = request.form.get('dokter_id')
        catatan = request.form.get('catatan')

        permintaan = PermintaanDarah(
            pasien_id=pasien_id,
            gol_darah_id=gol_darah_id,
            komponen=komponen,
            jumlah=jumlah,
            dokter_id=dokter_id,
            catatan=catatan
        )
        db.session.add(permintaan)
        db.session.commit()

        flash('Permintaan darah berhasil dibuat', 'success')
        return redirect(url_for('bank_darah.permintaan_list'))

    pasien_list = Pasien.query.filter(Pasien.aktif == True).all()
    gol_darah_list = GolonganDarah.query.filter(GolonganDarah.aktif == True).all()
    dokter_list = User.query.filter(User.role == 'dokter').all()
    return render_template('bank_darah/permintaan_baru.html', pasien_list=pasien_list, gol_darah_list=gol_darah_list, dokter_list=dokter_list)


@bank_darah_bp.route('/permintaan/<int:id>/setuju', methods=['POST'])
@login_required
def permintaan_setuju(id):
    permintaan = PermintaanDarah.query.get_or_404(id)

    # Check stock availability
    stok = StokDarah.query.filter_by(
        gol_darah_id=permintaan.gol_darah_id,
        komponen=permintaan.komponen,
        status='tersedia'
    ).first()

    if not stok or stok.jumlah < permintaan.jumlah:
        flash('Stok darah tidak mencukupi', 'danger')
        return redirect(url_for('bank_darah.permintaan_list'))

    # Reduce stock
    stok.jumlah -= permintaan.jumlah
    if stok.jumlah <= 0:
        stok.status = 'digunakan'

    # Create transaction
    transaksi = TransaksiDarah(
        stok_darah_id=stok.id,
        pasien_id=permintaan.pasien_id,
        permintaan_id=permintaan.id,
        dokter_pemeriksa_id=current_user.id
    )
    db.session.add(transaksi)

    # Update status
    permintaan.status = 'diberikan'

    db.session.commit()
    flash('Permintaan darah disetujui dan transfusi dilakukan', 'success')
    return redirect(url_for('bank_darah.permintaan_list'))


@bank_darah_bp.route('/permintaan/<int:id>/tolak', methods=['POST'])
@login_required
def permintaan_tolak(id):
    permintaan = PermintaanDarah.query.get_or_404(id)
    permintaan.status = 'ditolak'
    db.session.commit()

    flash('Permintaan darah ditolak', 'success')
    return redirect(url_for('bank_darah.permintaan_list'))


@bank_darah_bp.route('/expired')
@login_required
def expired_list():
    """List darah yang sudah/kedaluwarsa"""
    expired = StokDarah.query.filter(
        StokDarah.expire_date < date.today()
    ).all()

    return render_template('bank_darah/expired.html', expired=expired)


@bank_darah_bp.route('/api/stok')
@login_required
def api_stok():
    """JSON: get stok darah summary"""
    summary = {}
    for gol in ['A', 'B', 'AB', 'O']:
        gol_obj = GolonganDarah.query.filter_by(nama=gol).first()
        if gol_obj:
            summary[gol] = sum(s.jumlah for s in gol_obj.stok_darah if s.status == 'tersedia')

    return jsonify(summary)